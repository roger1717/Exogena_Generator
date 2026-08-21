#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Procesador de CSV para Retenciones en la Fuente

Este módulo procesa un archivo CSV de auxiliar contable y extrae
las retenciones en la fuente (cuentas 2365xx) para generar
el formato DIAN 1003.

Autor: [Tu nombre]
Fecha: 2026-08-21
Versión: 2.0.0
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.models.mapping_rule import MappingRule
from app.models.retencion import Retencion
from app.core.constants import obtener_regla_retencion

logger = logging.getLogger(__name__)


class RetencionCSVProcessor:
    """
    Procesador de archivos CSV para retenciones en la fuente.
    
    Lee un auxiliar contable en formato CSV y extrae las retenciones
    (cuentas 2365xx) para generar el formato DIAN 1003.
    """
    
    # Patrón para extraer tarifa del nombre de la cuenta
    TARIFA_PATTERN = re.compile(r'(\d+[.,]?\d*)%')
    
    def __init__(self, db: Session):
        """
        Inicializar el procesador
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.reglas = self._cargar_reglas()
    
    def _cargar_reglas(self) -> Dict[str, MappingRule]:
        """Cargar todas las reglas de mapeo desde la BD"""
        reglas = self.db.query(MappingRule).all()
        return {str(r.puc_code).strip(): r for r in reglas}
    
    def _detectar_columnas(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detectar automáticamente las columnas del CSV"""
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
        
        # Verificar columnas requeridas
        required = ['fecha', 'asiento', 'cuenta', 'nit', 'razon_social']
        missing = [f for f in required if f not in mapping]
        
        if missing:
            raise ValueError(
                f"No se detectaron las columnas: {missing}. "
                f"Columnas disponibles: {columns}"
            )
        
        return mapping
    
    def _cargar_csv(self, file_path: Path) -> pd.DataFrame:
        """Cargar archivo CSV con detección automática de codificación"""
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
    
    def _limpiar_puc(self, puc: str) -> str:
        """
        Limpiar el código PUC eliminando puntos y decimales
        
        Args:
            puc: Código PUC (ej: "236530.0" → "236530")
        
        Returns:
            str: Código PUC limpio
        """
        if not puc:
            return ""
        
        puc_str = str(puc).strip()
        # Eliminar punto decimal y ceros
        if '.' in puc_str:
            puc_str = puc_str.split('.')[0]
        puc_str = puc_str.strip()
        return puc_str
    
    def _extraer_tarifa(self, nombre_cuenta: str) -> float:
        """Extraer tarifa del nombre de la cuenta"""
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
    
    def _extraer_concepto(self, nombre_cuenta: str) -> str:
        """Extraer concepto del nombre de la cuenta"""
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
        else:
            return "Concepto Contable Múltiple"
    
    def _es_cuenta_retencion(self, cuenta: str) -> bool:
        """Verificar si una cuenta es de retención (2365xx)"""
        cuenta_limpia = self._limpiar_puc(cuenta)
        return cuenta_limpia.startswith('2365')
    
    def _obtener_periodo(self, fecha) -> str:
        """Obtener período YYYY-MM desde una fecha"""
        if isinstance(fecha, str):
            try:
                fecha = pd.to_datetime(fecha)
            except:
                fecha = datetime.now()
        elif not isinstance(fecha, (datetime, pd.Timestamp)):
            fecha = datetime.now()
        
        return fecha.strftime('%Y-%m')
    
    def _obtener_valor(self, row: pd.Series, mapping: Dict[str, str]) -> float:
        """Obtener el valor de la fila (débito o crédito)"""
        # Intentar con crédito primero
        if 'credito' in mapping and mapping['credito'] in row:
            valor = row.get(mapping['credito'], 0)
            if pd.notna(valor) and float(valor) != 0:
                return float(valor)
        
        # Intentar con débito
        if 'debito' in mapping and mapping['debito'] in row:
            valor = row.get(mapping['debito'], 0)
            if pd.notna(valor) and float(valor) != 0:
                return float(valor)
        
        return 0.0
    
    def procesar_archivo(
        self,
        file_path: Path,
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Procesar archivo CSV y extraer retenciones
        """
        # 1. Cargar archivo
        df = self._cargar_csv(file_path)
        logger.info(f"📄 Archivo cargado: {len(df)} registros")
        
        # 2. Detectar columnas
        if column_mapping:
            mapping = column_mapping
        else:
            mapping = self._detectar_columnas(df)
        logger.info(f"📋 Mapeo detectado: {mapping}")
        
        # 3. Filtrar cuentas de retención (2365xx)
        cuenta_col = mapping.get('cuenta')
        if not cuenta_col:
            raise ValueError("No se detectó la columna de cuenta")
        
        # Limpiar la columna de cuenta para filtrar
        df['cuenta_limpia'] = df[cuenta_col].astype(str).apply(self._limpiar_puc)
        df_retenciones = df[df['cuenta_limpia'].str.startswith('2365')].copy()
        
        logger.info(f"🔍 Retenciones encontradas: {len(df_retenciones)}")
        
        if len(df_retenciones) == 0:
            return [], {
                'total_registros': len(df),
                'total_retenciones': 0,
                'mensaje': 'No se encontraron cuentas de retención (2365xx)'
            }
        
        # 4. Procesar cada retención
        retenciones = []
        errores = []
        
        for idx, row in df_retenciones.iterrows():
            try:
                # Extraer datos
                fecha = row.get(mapping.get('fecha'))
                asiento = str(row.get(mapping.get('asiento', ''))).strip()
                cuenta_raw = str(row.get(cuenta_col)).strip()
                cuenta = self._limpiar_puc(cuenta_raw)
                nombre_cuenta = str(row.get(mapping.get('nombre_cuenta', ''))).strip()
                nit = str(row.get(mapping.get('nit', ''))).strip()
                razon_social = str(row.get(mapping.get('razon_social', ''))).strip()
                
                # Obtener valor
                valor = self._obtener_valor(row, mapping)
                
                if valor == 0:
                    continue
                
                # Validar datos
                if not nit or nit == 'nan':
                    errores.append({
                        'fila': idx + 2,
                        'error': 'NIT vacío',
                        'data': {'cuenta': cuenta, 'nombre_cuenta': nombre_cuenta}
                    })
                    continue
                
                # Buscar regla de mapeo
                regla = self.reglas.get(cuenta)
                concepto_dian = None
                tarifa = 0
                tope_minimo = 0
                activo = True
                
                if regla:
                    concepto_dian = regla.concepto_retencion
                    tarifa = float(regla.tarifa_retencion) if regla.tarifa_retencion else 0
                    tope_minimo = float(regla.tope_minimo) if regla.tope_minimo else 0
                    activo = regla.activo if regla.activo is not None else True
                else:
                    # Buscar en constants.py
                    regla_const = obtener_regla_retencion(cuenta)
                    if regla_const:
                        concepto_dian = regla_const.get('concepto_retencion')
                        tarifa = regla_const.get('tarifa_retencion', 0)
                        tope_minimo = regla_const.get('tope_minimo', 0)
                        activo = regla_const.get('activo', True)
                
                if not activo:
                    continue
                
                if not concepto_dian:
                    errores.append({
                        'fila': idx + 2,
                        'error': f'Cuenta {cuenta} sin concepto de retención',
                        'data': {'nit': nit, 'razon_social': razon_social, 'cuenta': cuenta}
                    })
                    continue
                
                # Extraer concepto contable y tarifa
                concepto_contable = self._extraer_concepto(nombre_cuenta)
                if tarifa == 0:
                    tarifa = self._extraer_tarifa(nombre_cuenta)
                
                # Calcular base gravable
                base_gravable = valor / tarifa if tarifa > 0 else 0
                
                # Validar tope mínimo
                if base_gravable < tope_minimo:
                    continue
                
                # Crear registro
                retencion_data = {
                    'fecha': fecha,
                    'comprobante': asiento,
                    'nit_tercero': nit,
                    'nombre_tercero': razon_social,
                    'perfil_tributario': 'Responsable IVA',
                    'concepto_contable': concepto_contable,
                    'concepto_dian': concepto_dian,
                    'base_gravable': round(base_gravable, 2),
                    'tarifa': round(tarifa, 4),
                    'valor_retenido': round(valor, 2),
                    'cuenta_pasivo': cuenta,
                    'formato_asignado': '1003',
                    'concepto_exogena': regla.exogena_concept if regla else None,
                    'periodo': self._obtener_periodo(fecha),
                    'estado': 'procesado'
                }
                
                retenciones.append(retencion_data)
                
                # Guardar en BD
                if self.db:
                    self._guardar_retencion(retencion_data)
                
            except Exception as e:
                errores.append({
                    'fila': idx + 2,
                    'error': str(e),
                    'data': {'cuenta': row.get(cuenta_col, '')}
                })
                logger.error(f"Error en fila {idx + 2}: {e}")
        
        # Commit
        if self.db:
            self.db.commit()
        
        # Resumen
        resumen = {
            'total_registros': len(df),
            'total_retenciones': len(retenciones),
            'total_retenido': sum(r['valor_retenido'] for r in retenciones),
            'errores': len(errores),
            'detalles_errores': errores[:10]
        }
        
        logger.info(f"✅ Retenciones procesadas: {len(retenciones)}")
        logger.info(f"⚠️ Errores: {len(errores)}")
        
        return retenciones, resumen
    
    def _guardar_retencion(self, retencion_data: Dict) -> Optional[Retencion]:
        """Guardar retención en base de datos"""
        try:
            if isinstance(retencion_data['fecha'], str):
                try:
                    retencion_data['fecha'] = pd.to_datetime(retencion_data['fecha'])
                except:
                    retencion_data['fecha'] = datetime.now()
            
            retencion = Retencion(**retencion_data)
            self.db.add(retencion)
            return retencion
        except Exception as e:
            logger.error(f"Error al guardar retención: {e}")
            return None
    
    def generar_formato_dian(
        self,
        retenciones: List[Dict],
        output_path: Path,
        formato: str = "1003"
    ) -> Path:
        """Generar archivo en formato DIAN 1003"""
        if not retenciones:
            raise ValueError("No hay retenciones para generar")
        
        retenciones_validas = [
            r for r in retenciones 
            if r.get('valor_retenido', 0) > 0
        ]
        
        if not retenciones_validas:
            raise ValueError("No hay retenciones con valor > 0")
        
        lineas = []
        for r in retenciones_validas:
            linea = (
                f"{formato}|"
                f"{r['nit_tercero']}|"
                f"{r['concepto_dian']}|"
                f"{r['base_gravable']:.2f}|"
                f"{r['valor_retenido']:.2f}|"
                f"{r['periodo']}"
            )
            lineas.append(linea)
        
        output_file = output_path / f"formato_{formato}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas))
        
        return output_file