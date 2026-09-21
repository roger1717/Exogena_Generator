#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Procesador de CSV para Retenciones en la Fuente

Extrae retenciones del auxiliar contable y las clasifica por tipo
(ReteFuente, ReteIVA, ReteICA) usando ReglasService.

Autor: [Tu nombre]
Fecha: 2026-09-21
Versión: 4.0.0
"""

import pandas as pd
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.constants import CONCEPTOS_RETENCION_DIAN
from app.services.reglas_service import ReglasService
from app.models.mapping_rule import MappingRule
from app.models.retencion import Retencion

logger = logging.getLogger(__name__)


# ============================================================================
# HELPERS DE NIT
# ============================================================================

def _limpiar_nit(nit: str) -> Tuple[str, Optional[int]]:
    """Limpia un NIT y extrae el DV si viene con guion."""
    nit_str = str(nit).strip()
    if '-' in nit_str:
        partes = nit_str.split('-')
        nit_base = ''.join(filter(str.isdigit, partes[0]))
        dv = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
        return nit_base, dv
    return ''.join(filter(str.isdigit, nit_str)), None


def _calcular_dv_nit(nit_base: str) -> int:
    """Calcula el DV de un NIT colombiano (módulo 11)."""
    pesos = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    suma = 0
    for i, digito in enumerate(reversed(nit_base)):
        suma += int(digito) * pesos[i % len(pesos)]
    residuo = suma % 11
    dv = 11 - residuo
    if dv == 11:
        dv = 0
    elif dv == 10:
        dv = 9
    return dv


def _validar_nit(nit: str) -> Tuple[bool, str]:
    """
    Valida un NIT colombiano.
    Retorna (es_valido, mensaje).
    """
    nit_base, dv_reportado = _limpiar_nit(nit)

    if len(nit_base) < 6:
        return False, f"NIT demasiado corto: {nit}"

    if dv_reportado is None:
        # Sin DV explícito, no podemos validar. Lo aceptamos pero avisamos.
        return True, f"NIT sin DV: {nit_base}"

    dv_calculado = _calcular_dv_nit(nit_base)
    if dv_calculado == dv_reportado:
        return True, f"NIT válido: {nit_base}-{dv_reportado}"
    return False, f"NIT inválido: DV esperado {dv_calculado}, reportado {dv_reportado}"


# ============================================================================
# PROCESADOR
# ============================================================================

class RetencionCSVProcessor:
    """
    Procesador de archivos CSV para retenciones en la fuente.

    Uso:
        processor = RetencionCSVProcessor(db)
        retenciones, resumen = processor.procesar_archivo(Path("auxiliar.csv"))
    """

    TARIFA_PATTERN = re.compile(r'(\d+[.,]?\d*)%')

    # Prefijos de cuentas PUC de retención
    PREFIJOS_RETENCION = ("2365", "2368")

    def __init__(self, db: Session):
        """Inicializar el procesador."""
        self.db = db
        self.reglas_service = ReglasService(db)

    # ========================================================================
    # CARGA DE ARCHIVO
    # ========================================================================

    def _cargar_csv(self, file_path: Path) -> pd.DataFrame:
        """Cargar archivo CSV con detección automática de codificación."""
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                df.columns = df.columns.str.strip()
                logger.info(f"Archivo cargado con encoding: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error al cargar con {encoding}: {e}")
                continue

        raise ValueError(f"No se pudo leer el archivo {file_path}")

    # ========================================================================
    # DETECCIÓN DE COLUMNAS
    # ========================================================================

    def _detectar_columnas(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detectar automáticamente las columnas del CSV."""
        columns = df.columns.tolist()
        mapping = {}

        patterns = {
            'fecha': ['fecha', 'date', 'fech', 'dia'],
            'asiento': ['asiento', 'comprobante', 'comp', 'doc', 'documento'],
            'cuenta': ['cuenta', 'puc', 'codigo', 'cod', 'cta'],
            'nombre_cuenta': ['nombre_cuenta', 'nombre cuenta', 'cuenta_nombre', 'descripcion_cuenta'],
            'nit': ['nit', 'n.i.t', 'identificacion', 'cedula', 'ruc', 'tercero'],
            'razon_social': ['razon_social', 'razon social', 'nombre', 'cliente', 'proveedor'],
            'debito': ['debito', 'debe', 'cargo', 'db'],
            'credito': ['credito', 'haber', 'abono', 'cr'],
        }

        for field, pattern_list in patterns.items():
            for col in columns:
                col_lower = col.lower().strip()
                for pattern in pattern_list:
                    if re.search(pattern, col_lower, re.IGNORECASE):
                        mapping[field] = col
                        break
                if field in mapping:
                    break

        required = ['fecha', 'asiento', 'cuenta', 'nit', 'razon_social']
        missing = [f for f in required if f not in mapping]

        if missing:
            raise ValueError(
                f"No se detectaron las columnas: {missing}. "
                f"Columnas disponibles: {columns}"
            )

        return mapping

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _limpiar_puc(self, puc: str) -> str:
        """Limpiar el código PUC eliminando puntos y decimales."""
        if not puc:
            return ""
        puc_str = str(puc).strip()
        if '.' in puc_str:
            puc_str = puc_str.split('.')[0]
        return puc_str.strip()

    def _extraer_tarifa(self, nombre_cuenta: str) -> float:
        """Extraer tarifa del nombre de la cuenta (fallback)."""
        if not nombre_cuenta:
            return 0.0
        match = self.TARIFA_PATTERN.search(str(nombre_cuenta))
        if match:
            try:
                porcentaje = match.group(1).replace(',', '.')
                return float(porcentaje) / 100
            except ValueError:
                return 0.0
        return 0.0

    def _extraer_concepto_contable(self, nombre_cuenta: str) -> str:
        """Extraer concepto contable del nombre de la cuenta."""
        if not nombre_cuenta:
            return "Concepto Contable Múltiple"

        nombre = str(nombre_cuenta).lower()

        if 'arrendamiento' in nombre:
            return "Arrendamientos"
        elif 'honorario' in nombre:
            return "Honorarios"
        elif 'servicio' in nombre:
            return "Servicios Generales"
        elif 'comision' in nombre:
            return "Comisiones"
        elif 'transporte' in nombre:
            return "Transporte de carga"
        elif 'reteiva' in nombre:
            return "ReteIVA"
        elif 'reteica' in nombre:
            return "ReteICA"
        return "Concepto Contable Múltiple"

    def _obtener_periodo(self, fecha) -> str:
        """Obtener período YYYY-MM desde una fecha."""
        if isinstance(fecha, str):
            try:
                fecha = pd.to_datetime(fecha)
            except Exception:
                fecha = datetime.now()
        elif not isinstance(fecha, (datetime, pd.Timestamp)):
            fecha = datetime.now()
        return fecha.strftime('%Y-%m')

    def _obtener_valor(self, row: pd.Series, mapping: Dict[str, str]) -> float:
        """Obtener el valor de la fila (débito o crédito)."""
        if 'credito' in mapping and mapping['credito'] in row:
            valor = row.get(mapping['credito'], 0)
            if pd.notna(valor) and float(valor) != 0:
                return float(valor)
        if 'debito' in mapping and mapping['debito'] in row:
            valor = row.get(mapping['debito'], 0)
            if pd.notna(valor) and float(valor) != 0:
                return float(valor)
        return 0.0

    # ========================================================================
    # LÓGICA DE CLASIFICACIÓN
    # ========================================================================

    def _determinar_tipo_y_concepto(
        self, cuenta: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Determina tipo de retención y concepto DIAN desde ReglasService.
        Solo procesa reglas con tipo_regla='retencion' (PUC 2365xx/2368xx).
        """
        cuenta_limpia = self._limpiar_puc(cuenta)

        # Defensa en profundidad: filtro rápido por prefijo del PUC
        if not cuenta_limpia.startswith(("2365", "2368")):
            return None, None

        regla = self.reglas_service.obtener_por_puc(cuenta_limpia)

        if not regla:
            return None, None
        if not regla.activo:
            return None, None
        if regla.tipo_regla != "retencion":
            return None, None
        if not regla.es_retencion():
            return None, None

        return regla.tipo_retencion, regla.concepto_retencion

    def _calcular_base_y_valor(
        self,
        valor_csv: float,
        tarifa: float,
        regla: MappingRule,
    ) -> Tuple[float, float]:
        """
        Calcula la base gravable y el valor retenido.

        El CSV del auxiliar típicamente trae el VALOR RETENIDO en la columna.
        Por lo tanto:
            base_gravable = valor_csv / tarifa
            valor_retenido = valor_csv

        Si en el futuro el CSV trae el valor total, ajustar aquí.

        Returns:
            (base_gravable, valor_retenido)
        """
        if tarifa <= 0:
            return 0.0, 0.0

        valor_retenido = round(valor_csv, 2)
        base_gravable = round(valor_csv / tarifa, 2)
        return base_gravable, valor_retenido

    # ========================================================================
    # PROCESAMIENTO PRINCIPAL
    # ========================================================================

    def procesar_archivo(
        self,
        file_path: Path,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[Dict], Dict]:
        """Procesar archivo CSV y extraer retenciones."""

        # 1. Cargar archivo
        df = self._cargar_csv(file_path)
        logger.info(f"📄 Archivo cargado: {len(df)} registros")

        # 2. Detectar columnas
        mapping = column_mapping or self._detectar_columnas(df)
        logger.info(f"📋 Mapeo detectado: {mapping}")

        # 3. Filtrar cuentas de retención
        cuenta_col = mapping.get('cuenta')
        if not cuenta_col:
            raise ValueError("No se detectó la columna de cuenta")

        df['cuenta_limpia'] = df[cuenta_col].astype(str).apply(self._limpiar_puc)
        df_retenciones = df[
            df['cuenta_limpia'].str.startswith(self.PREFIJOS_RETENCION)
        ].copy()
        logger.info(f"🔍 Retenciones encontradas: {len(df_retenciones)}")

        if len(df_retenciones) == 0:
            return [], {
                'total_registros': len(df),
                'total_retenciones': 0,
                'mensaje': 'No se encontraron cuentas de retención',
            }

        # 4. Procesar cada retención
        retenciones = []
        errores = []

        for idx, row in df_retenciones.iterrows():
            try:
                self._procesar_fila(
                    idx=idx,
                    row=row,
                    mapping=mapping,
                    cuenta_col=cuenta_col,
                    retenciones=retenciones,
                    errores=errores,
                )
            except Exception as e:
                errores.append({
                    'fila': idx + 2,
                    'error': str(e),
                    'data': {'cuenta': row.get(cuenta_col, '')},
                })
                logger.error(f"Error en fila {idx + 2}: {e}")

        # 5. Commit
        if self.db:
            self.db.commit()

        # 6. Resumen
        resumen = self._construir_resumen(df, retenciones, errores)
        logger.info(f"✅ Retenciones procesadas: {len(retenciones)}")
        logger.info(f"   Tipos: {resumen.get('tipos_retencion', {})}")
        logger.info(f"⚠️ Errores: {len(errores)}")

        return retenciones, resumen

    def _procesar_fila(
        self,
        idx: int,
        row: pd.Series,
        mapping: Dict[str, str],
        cuenta_col: str,
        retenciones: List[Dict],
        errores: List[Dict],
    ) -> None:
        """Procesa una fila individual."""

        # Extraer datos
        fecha = row.get(mapping.get('fecha'))
        asiento = str(row.get(mapping.get('asiento', ''))).strip()
        cuenta_raw = str(row.get(cuenta_col)).strip()
        cuenta = self._limpiar_puc(cuenta_raw)
        nombre_cuenta = str(row.get(mapping.get('nombre_cuenta', ''))).strip()
        nit = str(row.get(mapping.get('nit', ''))).strip()
        razon_social = str(row.get(mapping.get('razon_social', ''))).strip()

        valor = self._obtener_valor(row, mapping)

        if valor == 0:
            return

        if not nit or nit == 'nan':
            errores.append({
                'fila': idx + 2,
                'error': 'NIT vacío',
                'data': {'cuenta': cuenta, 'nombre_cuenta': nombre_cuenta},
            })
            return

        # Validar NIT
        nit_valido, msg_nit = _validar_nit(nit)
        if not nit_valido:
            errores.append({
                'fila': idx + 2,
                'error': msg_nit,
                'data': {'cuenta': cuenta, 'nit': nit},
            })
            return

        # Determinar tipo y concepto
        tipo_retencion, concepto_dian = self._determinar_tipo_y_concepto(cuenta)

        if not tipo_retencion or not concepto_dian:
            errores.append({
                'fila': idx + 2,
                'error': f"Cuenta {cuenta} sin regla válida o inactiva",
                'data': {'cuenta': cuenta, 'nombre_cuenta': nombre_cuenta},
            })
            return

        # Obtener regla completa
        regla = self.reglas_service.obtener_por_puc(cuenta)
        if not regla:
            errores.append({
                'fila': idx + 2,
                'error': f"Regla no encontrada para {cuenta}",
                'data': {'cuenta': cuenta},
            })
            return

        # Tarifa
        tarifa = float(regla.tarifa_retencion or 0)
        if tarifa == 0:
            tarifa = self._extraer_tarifa(nombre_cuenta)
            if tarifa == 0:
                errores.append({
                    'fila': idx + 2,
                    'error': f"No se pudo determinar tarifa para {cuenta}",
                    'data': {'cuenta': cuenta, 'nombre_cuenta': nombre_cuenta},
                })
                return

        # Calcular base y valor
        base_gravable, valor_retenido = self._calcular_base_y_valor(
            valor_csv=valor,
            tarifa=tarifa,
            regla=regla,
        )

        # Validar tope mínimo
        tope_minimo = float(regla.tope_minimo or 0)
        if base_gravable < tope_minimo:
            logger.debug(
                f"Fila {idx + 2}: base {base_gravable} < tope {tope_minimo}, omitida"
            )
            return

        # Concepto contable
        concepto_contable = self._extraer_concepto_contable(nombre_cuenta)

        # Construir registro
        retencion_data = {
            'fecha': fecha,
            'comprobante': asiento,
            'nit_tercero': nit,
            'nombre_tercero': razon_social,
            'perfil_tributario': 'Responsable IVA',
            'concepto_contable': concepto_contable,
            'concepto_dian': concepto_dian,
            'base_gravable': base_gravable,
            'tarifa': round(tarifa, 4),
            'valor_retenido': valor_retenido,
            'cuenta_pasivo': cuenta,
            'formato_asignado': '1003',
            'concepto_exogena': regla.exogena_concept,
            'periodo': self._obtener_periodo(fecha),
            'tipo_retencion': tipo_retencion,
            'estado': 'procesado',
        }

        retenciones.append(retencion_data)

        # Guardar en BD con detección de duplicados
        if self.db:
            self._guardar_retencion(retencion_data)

    # ========================================================================
    # PERSISTENCIA
    # ========================================================================

    def _guardar_retencion(self, retencion_data: Dict) -> Optional[Retencion]:
        """
        Guardar retención en BD con detección de duplicados.

        Un duplicado se define por:
            (comprobante, nit_tercero, concepto_dian, periodo, valor_retenido)
        """
        try:
            # Normalizar fecha
            if isinstance(retencion_data['fecha'], str):
                try:
                    retencion_data['fecha'] = pd.to_datetime(retencion_data['fecha'])
                except Exception:
                    retencion_data['fecha'] = datetime.now()

            # Detectar duplicado
            existe = self.db.query(Retencion).filter(
                Retencion.comprobante == retencion_data['comprobante'],
                Retencion.nit_tercero == retencion_data['nit_tercero'],
                Retencion.concepto_dian == retencion_data['concepto_dian'],
                Retencion.periodo == retencion_data['periodo'],
                Retencion.valor_retenido == retencion_data['valor_retenido'],
            ).first()

            if existe:
                logger.warning(
                    f"Duplicado ignorado: comprobante={retencion_data['comprobante']}, "
                    f"nit={retencion_data['nit_tercero']}, "
                    f"concepto={retencion_data['concepto_dian']}, "
                    f"periodo={retencion_data['periodo']}"
                )
                return None

            retencion = Retencion(**retencion_data)
            self.db.add(retencion)
            return retencion
        except Exception as e:
            logger.error(f"Error al guardar retención: {e}")
            return None

    # ========================================================================
    # RESUMEN
    # ========================================================================

    def _construir_resumen(
        self,
        df: pd.DataFrame,
        retenciones: List[Dict],
        errores: List[Dict],
    ) -> Dict[str, Any]:
        """Construye el resumen del procesamiento."""
        resumen = {
            'total_registros': len(df),
            'total_retenciones': len(retenciones),
            'total_retenido': sum(r['valor_retenido'] for r in retenciones),
            'total_base': sum(r['base_gravable'] for r in retenciones),
            'errores': len(errores),
            'detalles_errores': errores[:10],
        }

        # Conteo por tipo
        tipos: Dict[str, int] = {}
        for r in retenciones:
            tipo = r.get('tipo_retencion', 'desconocido')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        resumen['tipos_retencion'] = tipos

        return resumen