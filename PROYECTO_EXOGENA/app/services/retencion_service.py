
"""
Servicio de Retenciones en la Fuente

Procesa archivos de retenciones, genera reportes y
prepara datos para exógena.


"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.constants import (
    CONCEPTOS_RETENCION_DIAN,
    TARIFAS_RETENCION,
    PUC_RETENCIONES,
    PUC_A_CONCEPTO_RETENCION,
    TOPES_MINIMOS,
    FORMATO_EXOGENA_A_RETENCION,
)
from app.models.retencion import Retencion
from app.schemas.retencion import RetencionCreate, RetencionResponse
from app.utils.file_processor import FileProcessor


class RetencionService:
    """
    Servicio para procesar y gestionar retenciones en la fuente
    """
    
    def __init__(self, db: Session = None):
        """
        Inicializar el servicio
        
        Args:
            db: Sesión de base de datos (opcional)
        """
        self.db = db
        self.file_processor = FileProcessor()
    
    def procesar_desde_excel(
        self,
        file_path: Path,
        sheet_name: str = "Retenciones_Auxiliar"
    ) -> Dict:
        """
        Procesar retenciones desde un archivo Excel
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja
        
        Returns:
            Dict con resultados del procesamiento
        """
        # Leer archivo
        datos = self.file_processor.leer_excel(file_path, sheet_name=sheet_name)
        
        if not datos:
            return {
                "total_registros": 0,
                "procesados": 0,
                "errores": 0,
                "total_retenido": 0,
                "detalles": []
            }
        
        # Procesar cada fila
        procesados = []
        errores = []
        total_retenido = 0
        
        for idx, row in enumerate(datos):
            try:
                retencion = self._procesar_fila_excel(row, idx)
                if retencion:
                    procesados.append(retencion)
                    total_retenido += retencion['valor_retenido']
                    
                    # Guardar en BD si hay sesión
                    if self.db:
                        self._guardar_retencion(retencion)
            except Exception as e:
                errores.append({
                    "fila": idx + 2,  # +2 por cabecera y 0-index
                    "error": str(e)
                })
        
        # Si hay BD, hacer commit
        if self.db:
            self.db.commit()
        
        return {
            "total_registros": len(datos),
            "procesados": len(procesados),
            "errores": len(errores),
            "total_retenido": total_retenido,
            "detalles": procesados
        }
    
    def _procesar_fila_excel(self, row: Dict, idx: int) -> Optional[Dict]:
        """
        Procesar una fila del archivo Excel
        
        Args:
            row: Diccionario con los datos de la fila
            idx: Índice de la fila
        
        Returns:
            Dict con la retención procesada o None
        """
        # Validar datos requeridos
        if not row.get('NIT_Tercero'):
            raise ValueError(f"NIT del tercero no encontrado en fila {idx}")
        
        if row.get('Valor_Retenido', 0) == 0:
            return None
        
        # Obtener concepto DIAN desde el concepto contable
        concepto_contable = row.get('Concepto_Contable', '')
        concepto_dian = self._mapear_concepto_a_dian(concepto_contable)
        
        # Obtener cuenta PUC
        cuenta_pasivo = row.get('Cuenta_Pasivo', '')
        
        # Validar que la cuenta sea de retención
        if not self._es_cuenta_retencion(cuenta_pasivo):
            raise ValueError(f"Cuenta {cuenta_pasivo} no es de retención")
        
        # Crear registro
        return {
            'fecha': row.get('Fecha_Transaccion'),
            'comprobante': row.get('Comprobante'),
            'nit_tercero': str(row.get('NIT_Tercero')).strip(),
            'nombre_tercero': row.get('Razon_Social'),
            'perfil_tributario': row.get('Perfil_Tributario', ''),
            'concepto_contable': concepto_contable,
            'concepto_dian': concepto_dian,
            'base_gravable': float(row.get('Base_Gravable', 0)),
            'tarifa': float(row.get('Porcentaje_ReteFuente', 0)),
            'valor_retenido': float(row.get('Valor_Retenido', 0)),
            'cuenta_pasivo': cuenta_pasivo,
            'periodo': self._obtener_periodo(row.get('Fecha_Transaccion')),
            'estado': 'procesado'
        }
    
    def _mapear_concepto_a_dian(self, concepto_contable: str) -> str:
        """Mapear concepto contable a código DIAN"""
        mapa = {
            "Arrendamientos": "01",
            "Servicios Generales": "02",
            "Honorarios": "03",
            "Servicios Profesionales": "04",
            "Comisiones": "05",
            "Transporte de carga": "06",
        }
        return mapa.get(concepto_contable, "99")
    
    def _es_cuenta_retencion(self, cuenta: str) -> bool:
        """Verificar si una cuenta es de retención"""
        return cuenta.startswith('2365')
    
    def _obtener_periodo(self, fecha) -> str:
        """Obtener período YYYY-MM desde una fecha"""
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        elif isinstance(fecha, datetime):
            pass
        else:
            fecha = datetime.now()
        return fecha.strftime('%Y-%m')
    
    def _guardar_retencion(self, retencion_data: Dict) -> Optional[Retencion]:
        """Guardar retención en base de datos"""
        if not self.db:
            return None
        
        try:
            # Crear instancia del modelo
            retencion = Retencion(**retencion_data)
            self.db.add(retencion)
            return retencion
        except Exception as e:
            raise ValueError(f"Error al guardar retención: {str(e)}")
    
    def generar_formato_dian(
        self,
        retenciones: List[Dict],
        output_path: Path,
        formato: str = "1003"
    ) -> Path:
        """
        Generar archivo en formato DIAN
        
        Args:
            retenciones: Lista de retenciones procesadas
            output_path: Ruta de salida
            formato: Formato DIAN (1003)
        
        Returns:
            Path del archivo generado
        """
        if not retenciones:
            raise ValueError("No hay retenciones para generar")
        
        # Generar líneas del archivo
        lineas = []
        for r in retenciones:
            if r['valor_retenido'] > 0:
                linea = (
                    f"{formato}|"
                    f"{r['nit_tercero']}|"
                    f"{r['concepto_dian']}|"
                    f"{r['base_gravable']:.2f}|"
                    f"{r['valor_retenido']:.2f}|"
                    f"{r['periodo']}"
                )
                lineas.append(linea)
        
        # Guardar archivo
        output_file = output_path / f"formato_{formato}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas))
        
        return output_file
    
    def generar_reporte_excel(
        self,
        retenciones: List[Dict],
        output_path: Path
    ) -> Path:
        """
        Generar reporte de retenciones en Excel
        
        Args:
            retenciones: Lista de retenciones
            output_path: Ruta de salida
        
        Returns:
            Path del archivo generado
        """
        if not retenciones:
            raise ValueError("No hay retenciones para reportar")
        
        df = pd.DataFrame(retenciones)
        
        # Reordenar columnas
        columnas = [
            'fecha', 'comprobante', 'nit_tercero', 'nombre_tercero',
            'concepto_contable', 'concepto_dian', 'base_gravable',
            'tarifa', 'valor_retenido', 'cuenta_pasivo', 'periodo'
        ]
        df = df[[c for c in columnas if c in df.columns]]
        
        # Guardar
        output_file = output_path / f"reporte_retenciones_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(output_file, index=False, sheet_name='Retenciones')
        
        return output_file
    
    def obtener_resumen(self, retenciones: List[Dict]) -> Dict:
        """
        Obtener resumen de retenciones
        
        Args:
            retenciones: Lista de retenciones
        
        Returns:
            Dict con resumen
        """
        if not retenciones:
            return {}
        
        df = pd.DataFrame(retenciones)
        
        return {
            'total_retenciones': len(df),
            'total_retenido': df['valor_retenido'].sum(),
            'total_base': df['base_gravable'].sum(),
            'tarifa_promedio': df['tarifa'].mean() * 100,
            'por_concepto': df.groupby('concepto_contable').agg({
                'valor_retenido': ['count', 'sum']
            }).to_dict(),
            'por_periodo': df.groupby('periodo').agg({
                'valor_retenido': 'sum'
            }).to_dict()
        }