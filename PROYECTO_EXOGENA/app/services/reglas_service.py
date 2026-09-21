#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servicio de Reglas de Mapeo.

Responsabilidades:
  - Cargar reglas desde data/reglas/*.json
  - Validar coherencia contable
  - Hacer UPSERT idempotente en BD
  - Exponer consultas (por PUC, por tipo, activas)
  - Cachear en memoria

Uso típico:
    db = SessionLocal()
    service = ReglasService(db)

    # Recargar desde JSON
    resultado = service.recargar_desde_json()

    # Consultar
    regla = service.obtener_por_puc("236530")
    retenciones = service.obtener_reglas_retencion_estricto()
    gastos = service.obtener_reglas_gasto()
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.reglas_validator import ReglasValidator
from app.models.mapping_rule import MappingRule

logger = logging.getLogger(__name__)


# ============================================================================
# LOADER: Carga JSON sin tocar la BD
# ============================================================================

class ReglasLoader:
    """Carga reglas desde JSON sin tocar la BD."""

    ARCHIVOS_ESPERADOS = ["renta.json", "iva.json", "ica.json", "exogena.json"]

    def __init__(self, reglas_dir: Path = Path("data/reglas")):
        self.reglas_dir = Path(reglas_dir)

    def cargar_todas(self, validar: bool = True) -> List[Dict[str, Any]]:
        """
        Carga los 4 JSON, los concatena y (opcionalmente) valida.

        Raises:
            FileNotFoundError: si falta algún archivo.
            ValueError: si hay errores de validación contable.
        """
        reglas: List[Dict[str, Any]] = []

        for nombre_archivo in self.ARCHIVOS_ESPERADOS:
            path = self.reglas_dir / nombre_archivo
            if not path.exists():
                raise FileNotFoundError(f"No se encontró {path}")
            reglas.extend(self._cargar_archivo(path))

        if validar:
            validator = ReglasValidator()
            errores = validator.validar_todas(reglas)
            if errores:
                msg = (
                    f"Reglas inválidas ({len(errores)} errores):\n"
                    + "\n".join(errores)
                )
                raise ValueError(msg)

        return reglas

    def _cargar_archivo(self, path: Path) -> List[Dict]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("reglas", [])

    def resumen(self, reglas: Optional[List[Dict]] = None) -> Dict[str, int]:
        if reglas is None:
            reglas = self.cargar_todas(validar=False)
        return ReglasValidator().resumen(reglas)


# ============================================================================
# SERVICE: Carga a BD + consultas con cache
# ============================================================================

class ReglasService:
    """
    Servicio de reglas de mapeo.

    Uso:
        db = SessionLocal()
        service = ReglasService(db)
        resultado = service.recargar_desde_json()
    """

    # Campos del modelo que se mapean desde el JSON
    CAMPOS_MODELO = [
        "puc_name",
        "exogena_format",
        "exogena_concept",
        "exogena_concept_name",
        "concepto_retencion",
        "tarifa_retencion",
        "tope_minimo",
        "aplica_iva",
        "tipo_retencion",
        "tipo_regla",           # ← NUEVO
        "calcula_base_sobre",
        "cliente",
        "activo",
    ]

    # Cache a nivel de clase (compartido entre instancias)
    _cache_por_puc: Optional[Dict[str, MappingRule]] = None

    def __init__(self, db: Session, reglas_dir: Path = Path("data/reglas")):
        self.db = db
        self.loader = ReglasLoader(reglas_dir)

    # ========================================================================
    # CARGA A BD (UPSERT)
    # ========================================================================

    def recargar_desde_json(self, validar: bool = True) -> Dict[str, int]:
        """
        Carga los 4 JSON a la BD con UPSERT idempotente.

        Returns:
            Dict con {creadas, actualizadas, sin_cambios, total}.
        """
        reglas = self.loader.cargar_todas(validar=validar)

        creadas = actualizadas = sin_cambios = 0

        for regla_data in reglas:
            puc = str(regla_data.get("puc_code", "")).strip()
            if not puc:
                continue

            existente = (
                self.db.query(MappingRule)
                .filter(MappingRule.puc_code == puc)
                .first()
            )
            campos = self._mapear_a_modelo(regla_data)

            if existente:
                if self._hubo_cambios(existente, campos):
                    for k, v in campos.items():
                        setattr(existente, k, v)
                    actualizadas += 1
                else:
                    sin_cambios += 1
            else:
                self.db.add(MappingRule(puc_code=puc, **campos))
                creadas += 1

        self.db.commit()

        # Invalidar cache
        ReglasService._cache_por_puc = None

        logger.info(
            f"Reglas cargadas: creadas={creadas}, "
            f"actualizadas={actualizadas}, sin_cambios={sin_cambios}"
        )

        return {
            "creadas": creadas,
            "actualizadas": actualizadas,
            "sin_cambios": sin_cambios,
            "total": creadas + actualizadas + sin_cambios,
        }

    def _mapear_a_modelo(self, regla_data: Dict) -> Dict[str, Any]:
        """Mapea un dict del JSON a campos del modelo."""
        mapeo = {}
        for campo in self.CAMPOS_MODELO:
            valor = regla_data.get(campo)
            # Normalizar tipos
            if campo in ("tarifa_retencion", "tope_minimo") and valor is not None:
                valor = Decimal(str(valor))
            mapeo[campo] = valor

        # Defaults
        mapeo.setdefault("aplica_iva", False)
        mapeo.setdefault("tipo_regla", "retencion")
        mapeo.setdefault("calcula_base_sobre", "valor")
        mapeo.setdefault("activo", True)
        return mapeo

    def _hubo_cambios(self, existente: MappingRule, campos: Dict) -> bool:
        """Compara el modelo existente con los campos nuevos."""
        for k, v in campos.items():
            actual = getattr(existente, k, None)
            # Normalizar Decimal
            if isinstance(v, Decimal) and actual is not None:
                actual = Decimal(str(actual))
            if actual != v:
                return True
        return False

    # ========================================================================
    # CONSULTAS CON CACHE
    # ========================================================================

    def obtener_por_puc(self, puc_code: str) -> Optional[MappingRule]:
        """Obtiene una regla por PUC (usa cache)."""
        cache = self._get_cache()
        return cache.get(str(puc_code).strip())

    def obtener_reglas_activas(self) -> List[MappingRule]:
        """Retorna todas las reglas activas."""
        return list(self._get_cache().values())

    def obtener_reglas_retencion(self, estricto: bool = True) -> List[MappingRule]:
        """
        Retorna reglas que aplican retención.

        Args:
            estricto: Si True (default), solo reglas con tipo_regla='retencion'.
                      Si False, cualquier regla con concepto_retencion.
        """
        if estricto:
            return self.obtener_reglas_retencion_estricto()
        return [r for r in self._get_cache().values() if r.es_retencion()]

    def obtener_reglas_retencion_estricto(self) -> List[MappingRule]:
        """
        Retorna SOLO las reglas cuyo PUC es una cuenta de retención (2365xx/2368xx).
        Excluye reglas de gasto aunque tengan concepto_retencion.
        """
        return [
            r for r in self._get_cache().values()
            if r.tipo_regla == "retencion" and r.es_retencion()
        ]

    def obtener_reglas_por_tipo(self, tipo: str) -> List[MappingRule]:
        """Retorna reglas de un tipo específico (renta, iva, ica)."""
        return [
            r for r in self._get_cache().values()
            if r.tipo_retencion == tipo and r.es_retencion()
        ]

    def obtener_reglas_por_cliente(self, cliente: str) -> List[MappingRule]:
        """Retorna reglas ICA específicas de un cliente."""
        cliente_upper = cliente.upper()
        return [
            r for r in self._get_cache().values()
            if r.cliente and r.cliente.upper() == cliente_upper
        ]

    def obtener_reglas_gasto(self) -> List[MappingRule]:
        """Retorna reglas de tipo gasto (cuentas 5xxxxx)."""
        return [
            r for r in self._get_cache().values()
            if r.tipo_regla == "gasto"
        ]

    def obtener_reglas_exogena(self) -> List[MappingRule]:
        """Retorna reglas de tipo exógena pura."""
        return [
            r for r in self._get_cache().values()
            if r.tipo_regla == "exogena"
        ]

    def es_cuenta_retencion(self, puc_code: str) -> bool:
        """
        Verifica si un PUC es una cuenta de retención válida.
        NO basta con que tenga concepto_retencion: debe ser tipo_regla='retencion'.
        """
        regla = self.obtener_por_puc(puc_code)
        if not regla:
            return False
        return regla.tipo_regla == "retencion" and regla.es_retencion()

    # ========================================================================
    # CACHE
    # ========================================================================

    def _get_cache(self) -> Dict[str, MappingRule]:
        """Obtiene (o construye) el cache de reglas activas."""
        if ReglasService._cache_por_puc is None:
            reglas = (
                self.db.query(MappingRule)
                .filter(MappingRule.activo == True)  # noqa: E712
                .all()
            )
            ReglasService._cache_por_puc = {r.puc_code: r for r in reglas}
        return ReglasService._cache_por_puc

    @classmethod
    def invalidar_cache(cls) -> None:
        """Invalida el cache (llamar después de cambios)."""
        cls._cache_por_puc = None

    # ========================================================================
    # ESTADÍSTICAS
    # ========================================================================

    def estadisticas(self) -> Dict[str, int]:
        """
        Retorna estadísticas de las reglas en BD.

        Returns:
            Dict con conteos por tipo_regla y tipo_retencion.
        """
        cache = self._get_cache()
        stats = {
            "total": len(cache),
            "retencion": 0,
            "gasto": 0,
            "exogena": 0,
            "renta": 0,
            "iva": 0,
            "ica": 0,
        }
        for r in cache.values():
            tipo_regla = r.tipo_regla or "exogena"
            if tipo_regla in ("retencion", "gasto", "exogena"):
                stats[tipo_regla] += 1

            if tipo_regla == "retencion" and r.tipo_retencion in ("renta", "iva", "ica"):
                stats[r.tipo_retencion] += 1

        return stats