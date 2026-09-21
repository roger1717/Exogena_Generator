#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validador de reglas de mapeo contable.

Verifica coherencia contable antes de cargar reglas a la BD.
Se usa desde scripts, servicios y tests.

Reglas que valida:
  1. Campos obligatorios (puc_code, exogena_format, exogena_concept)
  2. Duplicados de PUC
  3. Tipo de retención válido (renta | iva | ica)
  4. Coherencia concepto_retencion ↔ tipo_retencion
  5. Coherencia tipo_retencion ↔ calcula_base_sobre
  6. Coherencia tipo_regla ↔ prefijo del PUC
  7. Tarifas en rango [0, 1]
  8. Topes mínimos no negativos
  9. Consistencia de campos opcionales (tipo sin concepto, etc.)
"""

from typing import Dict, List, Any

from app.core.constants import (
    CONCEPTOS_POR_TIPO,
    TIPOS_RETENCION,
    CALCULA_BASE_SOBRE_VALORES,
)


class ReglasValidator:
    """
    Valida coherencia contable de las reglas de mapeo.

    Uso:
        validator = ReglasValidator()
        errores = validator.validar_todas(reglas)
        if errores:
            raise ValueError("\\n".join(errores))
    """

    # Valores permitidos
    TIPOS_RETENCION_VALIDOS = set(TIPOS_RETENCION.keys())  # renta, iva, ica
    CALCULA_BASE_VALIDOS = set(CALCULA_BASE_SOBRE_VALORES.keys())  # valor, total, iva
    TIPOS_REGLA_VALIDOS = {"retencion", "gasto", "exogena"}

    # Prefijos de PUC por tipo de regla
    PREFIJOS_RETENCION = ("2365", "2368")
    PREFIJO_GASTO = "5"

    def __init__(self, estricto: bool = True):
        """
        Args:
            estricto: Si True, considera errores los casos dudosos.
                      Si False, solo errores graves.
        """
        self.estricto = estricto

    # ========================================================================
    # API PÚBLICA
    # ========================================================================

    def validar_todas(self, reglas: List[Dict[str, Any]]) -> List[str]:
        """Valida una lista completa de reglas. Retorna lista de errores."""
        errores: List[str] = []

        # 1. Duplicados
        errores.extend(self._validar_duplicados(reglas))

        # 2. Reglas individuales
        for regla in reglas:
            errores.extend(self._validar_regla(regla))

        return errores

    def validar_una(self, regla: Dict[str, Any]) -> List[str]:
        """Valida una sola regla."""
        return self._validar_regla(regla)

    def resumen(self, reglas: List[Dict]) -> Dict[str, int]:
        """Retorna conteo de reglas por tipo_regla y tipo_retencion."""
        conteo = {
            "total": len(reglas),
            "retencion": 0,
            "gasto": 0,
            "exogena": 0,
            "renta": 0,
            "iva": 0,
            "ica": 0,
        }
        for r in reglas:
            tipo_regla = r.get("tipo_regla") or "exogena"
            if tipo_regla in conteo:
                conteo[tipo_regla] += 1

            tipo_ret = r.get("tipo_retencion")
            if tipo_ret in ("renta", "iva", "ica"):
                conteo[tipo_ret] += 1

        return conteo

    # ========================================================================
    # VALIDACIONES DE LISTA
    # ========================================================================

    def _validar_duplicados(self, reglas: List[Dict]) -> List[str]:
        """Detecta PUC duplicados."""
        vistos: Dict[str, int] = {}
        errores = []

        for i, r in enumerate(reglas):
            puc = r.get("puc_code")
            if not puc:
                continue

            if puc in vistos:
                errores.append(
                    f"PUC duplicado: '{puc}' en índice {i} "
                    f"(ya visto en índice {vistos[puc]})"
                )
            else:
                vistos[puc] = i

        return errores

    # ========================================================================
    # VALIDACIÓN DE REGLA INDIVIDUAL
    # ========================================================================

    def _validar_regla(self, regla: Dict) -> List[str]:
        """Valida una regla individual."""
        errores: List[str] = []
        puc = regla.get("puc_code", "<sin_puc>")

        def err(msg: str) -> None:
            errores.append(f"[{puc}] {msg}")

        # --------------------------------------------------------------------
        # 1. Campos obligatorios
        # --------------------------------------------------------------------
        if not puc:
            err("puc_code es obligatorio")
        if not regla.get("exogena_format"):
            err("exogena_format es obligatorio")
        if not regla.get("exogena_concept"):
            err("exogena_concept es obligatorio")

        # --------------------------------------------------------------------
        # 2. Tipos válidos
        # --------------------------------------------------------------------
        tipo = regla.get("tipo_retencion")
        concepto = regla.get("concepto_retencion")
        calcula = regla.get("calcula_base_sobre")
        tipo_regla = regla.get("tipo_regla")

        if tipo is not None and tipo not in self.TIPOS_RETENCION_VALIDOS:
            err(f"tipo_retencion inválido: '{tipo}'. "
                f"Válidos: {sorted(self.TIPOS_RETENCION_VALIDOS)}")

        if calcula is not None and calcula not in self.CALCULA_BASE_VALIDOS:
            err(f"calcula_base_sobre inválido: '{calcula}'. "
                f"Válidos: {sorted(self.CALCULA_BASE_VALIDOS)}")

        if tipo_regla is not None and tipo_regla not in self.TIPOS_REGLA_VALIDOS:
            err(f"tipo_regla inválido: '{tipo_regla}'. "
                f"Válidos: {sorted(self.TIPOS_REGLA_VALIDOS)}")

        # --------------------------------------------------------------------
        # 3. Coherencia tipo_retencion ↔ concepto_retencion
        # --------------------------------------------------------------------
        if tipo and concepto:
            if concepto not in CONCEPTOS_POR_TIPO.get(tipo, set()):
                err(
                    f"concepto '{concepto}' no corresponde a tipo '{tipo}'. "
                    f"Válidos para {tipo}: {sorted(CONCEPTOS_POR_TIPO[tipo])}"
                )

        # --------------------------------------------------------------------
        # 4. Coherencia tipo_retencion ↔ calcula_base_sobre
        # --------------------------------------------------------------------
        if tipo == "ica":
            if calcula != "total":
                err(f"ICA requiere calcula_base_sobre='total', "
                    f"tiene '{calcula or 'None'}'")
        elif tipo == "iva":
            if calcula != "iva":
                err(f"IVA requiere calcula_base_sobre='iva', "
                    f"tiene '{calcula or 'None'}'")
        elif tipo == "renta":
            if calcula is not None and calcula not in ("valor", "total"):
                err(f"renta con calcula_base_sobre='{calcula}' no esperado")

        # --------------------------------------------------------------------
        # 5. Coherencia tipo_regla ↔ prefijo del PUC
        # --------------------------------------------------------------------
        if tipo_regla == "retencion":
            if not puc.startswith(self.PREFIJOS_RETENCION):
                err(
                    f"tipo_regla='retencion' pero PUC '{puc}' "
                    f"no empieza con {self.PREFIJOS_RETENCION}"
                )
        elif tipo_regla == "gasto":
            if not puc.startswith(self.PREFIJO_GASTO):
                err(
                    f"tipo_regla='gasto' pero PUC '{puc}' "
                    f"no empieza con '{self.PREFIJO_GASTO}'"
                )
        elif tipo_regla == "exogena":
            if puc.startswith(self.PREFIJOS_RETENCION):
                err(f"tipo_regla='exogena' pero PUC '{puc}' es de retención")

        # --------------------------------------------------------------------
        # 6. Consistencia tipo_regla ↔ campos de retención
        # --------------------------------------------------------------------
        if tipo_regla == "retencion":
            if not tipo:
                err("tipo_regla='retencion' pero falta tipo_retencion")
            if not concepto:
                err("tipo_regla='retencion' pero falta concepto_retencion")
            if regla.get("tarifa_retencion") is None:
                err("tipo_regla='retencion' pero falta tarifa_retencion")

        if tipo_regla == "gasto":
            # Un gasto mapea a un concepto de retención (para saber qué se debió retener)
            if not concepto:
                err("tipo_regla='gasto' requiere concepto_retencion (mapea el gasto)")

        if tipo_regla == "exogena":
            if tipo is not None:
                if self.estricto:
                    err("tipo_regla='exogena' no debería tener tipo_retencion")
            if concepto is not None:
                if self.estricto:
                    err("tipo_regla='exogena' no debería tener concepto_retencion")

        # --------------------------------------------------------------------
        # 7. Tarifa en rango [0, 1]
        # --------------------------------------------------------------------
        tarifa = regla.get("tarifa_retencion")
        if tarifa is not None:
            try:
                tarifa_f = float(tarifa)
                if not (0 <= tarifa_f <= 1):
                    err(f"tarifa fuera de rango [0, 1]: {tarifa_f}")
            except (TypeError, ValueError):
                err(f"tarifa no numérica: {tarifa}")

        # --------------------------------------------------------------------
        # 8. Tope mínimo no negativo
        # --------------------------------------------------------------------
        tope = regla.get("tope_minimo")
        if tope is not None:
            try:
                tope_f = float(tope)
                if tope_f < 0:
                    err(f"tope_minimo no puede ser negativo: {tope_f}")
            except (TypeError, ValueError):
                err(f"tope_minimo no numérico: {tope}")

        # --------------------------------------------------------------------
        # 9. Si tiene tipo_retencion, debe tener concepto_retencion
        # --------------------------------------------------------------------
        if tipo and not concepto:
            err(f"tiene tipo_retencion='{tipo}' pero falta concepto_retencion")

        # --------------------------------------------------------------------
        # 10. Si tiene concepto_retencion, debe tener tipo_retencion
        # --------------------------------------------------------------------
        if concepto and not tipo:
            err(f"tiene concepto_retencion='{concepto}' pero falta tipo_retencion")

        # --------------------------------------------------------------------
        # 11. Reglas de exógena pura no deben tener tarifa ni tope
        # --------------------------------------------------------------------
        if tipo_regla == "exogena":
            if tarifa is not None and self.estricto:
                err("regla de exógena pura no debería tener tarifa_retencion")
            if tope is not None and self.estricto:
                err("regla de exógena pura no debería tener tope_minimo")

        # --------------------------------------------------------------------
        # 12. ICA específico (236810-236819) requiere cliente
        # --------------------------------------------------------------------
        if tipo == "ica" and puc:
            if "236810" <= puc <= "236819":
                if not regla.get("cliente"):
                    err(f"ICA específico ({puc}) requiere campo 'cliente'")

        return errores