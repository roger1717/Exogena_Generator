
"""
Servicio de Retenciones en la Fuente

Procesa archivos de retenciones, genera reportes y
prepara datos para exógena.


"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.constants import (
    FORMATO_EXOGENA_A_RETENCION,
    CONCEPTO_CONTABLE_A_DIAN,
    get_tarifa_retencion,
    get_tope_minimo,
    es_cuenta_retencion,
    obtener_regla_retencion,
    REGLAS_RETENCION,
)
from app.models.retencion import Retencion
from app.models.mapping_rule import MappingRule
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
    
    def obtener_regla(self, puc_code: str) -> Optional[Dict]:
        """
        Obtener regla de mapeo (primero de BD, luego de constants)
        
        Args:
            puc_code: Código PUC a buscar
        
        Returns:
            Dict con la regla o None
        """
        # 1. Intentar desde BD
        if self.db:
            regla_bd = self.db.query(MappingRule).filter(
                MappingRule.puc_code == puc_code
            ).first()
            
            if regla_bd:
                return {
                    'puc_code': regla_bd.puc_code,
                    'puc_name': regla_bd.puc_name,
                    'exogena_format': regla_bd.exogena_format,
                    'exogena_concept': regla_bd.exogena_concept,
                    'exogena_concept_name': regla_bd.exogena_concept_name,
                    'concepto_retencion': regla_bd.concepto_retencion,
                    'tarifa_retencion': float(regla_bd.tarifa_retencion) if regla_bd.tarifa_retencion else None,
                    'tope_minimo': float(regla_bd.tope_minimo) if regla_bd.tope_minimo else 0,
                    'aplica_iva': regla_bd.aplica_iva or False,
                    'tipo_retencion': regla_bd.tipo_retencion,
                    'activo': regla_bd.activo if regla_bd.activo is not None else True
                }
        
        # 2. Fallback a constants.py
        return obtener_regla_retencion(puc_code)
    
    def procesar_desde_excel(
        self,
        file_path: Path,
        sheet_name: str = "Retenciones_Auxiliar"
    ) -> Dict[str, Any]:
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
                # Validar datos requeridos
                nit = row.get('NIT_Tercero')
                if not nit:
                    errores.append({
                        "fila": idx + 2,
                        "error": "NIT del tercero no encontrado"
                    })
                    continue
                
                valor_retenido = row.get('Valor_Retenido', 0)
                if not valor_retenido or float(valor_retenido) == 0:
                    continue
                
                # Obtener cuenta PUC
                cuenta_pasivo = row.get('Cuenta_Pasivo', '')
                
                # 1. Obtener regla desde BD o constants
                regla = self.obtener_regla(cuenta_pasivo)
                
                if not regla:
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} no tiene regla de mapeo"
                    })
                    continue
                
                # 2. Verificar si es cuenta de retención
                if not regla.get('activo', True):
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} está inactiva"
                    })
                    continue
                
                concepto_retencion = regla.get('concepto_retencion')
                if not concepto_retencion:
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} no tiene concepto de retención"
                    })
                    continue
                
                # 3. Validar tope mínimo
                base_gravable = float(row.get('Base_Gravable', 0))
                tope_minimo = regla.get('tope_minimo', 0)
                
                if base_gravable < tope_minimo:
                    # No aplica retención por tope mínimo
                    continue
                
                # 4. Obtener tarifa
                tarifa = regla.get('tarifa_retencion', float(row.get('Porcentaje_ReteFuente', 0)))
                
                # 5. Obtener concepto contable
                concepto_contable = row.get('Concepto_Contable', '')
                
                # 6. Crear registro
                retencion_data = {
                    'fecha': row.get('Fecha_Transaccion'),
                    'comprobante': row.get('Comprobante'),
                    'nit_tercero': str(nit).strip(),
                    'nombre_tercero': row.get('Razon_Social'),
                    'perfil_tributario': row.get('Perfil_Tributario', ''),
                    'concepto_contable': concepto_contable,
                    'concepto_dian': concepto_retencion,
                    'base_gravable': base_gravable,
                    'tarifa': tarifa,
                    'valor_retenido': float(valor_retenido),
                    'cuenta_pasivo': cuenta_pasivo,
                    'formato_asignado': FORMATO_EXOGENA_A_RETENCION.get(
                        regla.get('exogena_format', '1001'), '1003'
                    ),
                    'concepto_exogena': regla.get('exogena_concept'),
                    'periodo': self._obtener_periodo(row.get('Fecha_Transaccion')),
                    'estado': 'procesado'
                }
                
                procesados.append(retencion_data)
                total_retenido += retencion_data['valor_retenido']
                
                # Guardar en BD si hay sesión
                if self.db:
                    self._guardar_retencion(retencion_data)
                    
            except Exception as e:
                errores.append({
                    "fila": idx + 2,
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
    
    def _obtener_periodo(self, fecha) -> str:
        """Obtener período YYYY-MM desde una fecha"""
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                fecha = datetime.now()
        elif not isinstance(fecha, datetime):
            fecha = datetime.now()
        return fecha.strftime('%Y-%m')
    
    def _guardar_retencion(self, retencion_data: Dict) -> Optional[Retencion]:
        """Guardar retención en base de datos"""
        if not self.db:
            return None
        
        try:
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
            if r.get('valor_retenido', 0) > 0:
                # Formato: TipoRegistro|NIT|Concepto|Base|ValorRetenido|Periodo
                linea = (
                    f"{formato}|"
                    f"{r['nit_tercero']}|"
                    f"{r['concepto_dian']}|"
                    f"{r['base_gravable']:.2f}|"
                    f"{r['valor_retenido']:.2f}|"
                    f"{r['periodo']}"
                )
                lineas.append(linea)
        
        if not lineas:
            raise ValueError("No hay retenciones con valor > 0 para generar")
        
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
            'tarifa', 'valor_retenido', 'cuenta_pasivo', 'periodo', 'estado'
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
            'total_retenido': float(df['valor_retenido'].sum()),
            'total_base': float(df['base_gravable'].sum()),
            'tarifa_promedio': float(df['tarifa'].mean() * 100),
            'por_concepto': df.groupby('concepto_dian').agg({
                'valor_retenido': ['count', 'sum']
            }).to_dict(),
            'por_periodo': df.groupby('periodo').agg({
                'valor_retenido': 'sum'
            }).to_dict()
        }
    
    def obtener_retenciones_por_periodo(self, periodo: str) -> List[Dict]:
        """
        Obtener retenciones de la BD por período
        
        Args:
            periodo: Período en formato YYYY-MM
        
        Returns:
            Lista de retenciones
        """
        if not self.db:
            return []
        
        retenciones = self.db.query(Retencion).filter(
            Retencion.periodo == periodo
        ).all()
        
        return [r.to_dict() for r in retenciones]