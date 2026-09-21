#!/usr/bin/env python
# app/services/retencion_service.py
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

from app.services.excel_generator import ExcelGenerator
from app.services.reglas_service import ReglasService

from app.core.constants import (
    FORMATO_EXOGENA_A_RETENCION,
    CONCEPTO_CONTABLE_A_DIAN,
)

from app.models.retencion import Retencion
from app.models.mapping_rule import MappingRule
from app.utils.file_processor import FileProcessor


class RetencionService:
    """
    Servicio para procesar y gestionar retenciones en la fuente
    """

    def __init__(self, db: Session = None):
        self.db = db
        self.file_processor = FileProcessor()
        self._reglas_service: Optional[ReglasService] = None

    @property
    def reglas_service(self) -> Optional[ReglasService]:
        """Lazy init del ReglasService."""
        if self.db and self._reglas_service is None:
            self._reglas_service = ReglasService(self.db)
        return self._reglas_service

    def obtener_regla(self, puc_code: str) -> Optional[MappingRule]:
        """
        Obtiene la regla desde ReglasService (con cache).

        Returns:
            MappingRule o None si no existe.
        """
        if not self.reglas_service:
            return None
        return self.reglas_service.obtener_por_puc(puc_code)

    def procesar_desde_excel(
        self,
        file_path: Path,
        sheet_name: str = "Retenciones_Auxiliar"
    ) -> Dict[str, Any]:
        """Procesar retenciones desde un archivo Excel."""
        datos = self.file_processor.leer_excel(file_path, sheet_name=sheet_name)

        if not datos:
            return {
                "total_registros": 0,
                "procesados": 0,
                "errores": 0,
                "total_retenido": 0,
                "detalles": []
            }

        procesados = []
        errores = []
        total_retenido = 0

        for idx, row in enumerate(datos):
            try:
                nit = row.get('NIT_Tercero')
                if not nit:
                    errores.append({"fila": idx + 2, "error": "NIT del tercero no encontrado"})
                    continue

                valor_retenido = row.get('Valor_Retenido', 0)
                if not valor_retenido or float(valor_retenido) == 0:
                    continue

                cuenta_pasivo = row.get('Cuenta_Pasivo', '')
                regla = self.obtener_regla(cuenta_pasivo)

                if not regla:
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} no tiene regla de mapeo"
                    })
                    continue

                if not regla.activo:
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} está inactiva"
                    })
                    continue

                if not regla.concepto_retencion:
                    errores.append({
                        "fila": idx + 2,
                        "error": f"Cuenta {cuenta_pasivo} no tiene concepto de retención"
                    })
                    continue

                base_gravable = float(row.get('Base_Gravable', 0))
                tope_minimo = float(regla.tope_minimo or 0)

                if base_gravable < tope_minimo:
                    continue

                tarifa = float(regla.tarifa_retencion or 0)
                if tarifa == 0:
                    tarifa = float(row.get('Porcentaje_ReteFuente', 0))

                retencion_data = {
                    'fecha': row.get('Fecha_Transaccion'),
                    'comprobante': row.get('Comprobante'),
                    'nit_tercero': str(nit).strip(),
                    'nombre_tercero': row.get('Razon_Social'),
                    'perfil_tributario': row.get('Perfil_Tributario', ''),
                    'concepto_contable': row.get('Concepto_Contable', ''),
                    'concepto_dian': regla.concepto_retencion,
                    'base_gravable': base_gravable,
                    'tarifa': tarifa,
                    'valor_retenido': float(valor_retenido),
                    'cuenta_pasivo': cuenta_pasivo,
                    'tipo_retencion': regla.tipo_retencion or 'renta',
                    'formato_asignado': FORMATO_EXOGENA_A_RETENCION.get(
                        regla.exogena_format, '1003'
                    ),
                    'concepto_exogena': regla.exogena_concept,
                    'periodo': self._obtener_periodo(row.get('Fecha_Transaccion')),
                    'estado': 'procesado'
                }

                procesados.append(retencion_data)
                total_retenido += retencion_data['valor_retenido']

                if self.db:
                    self._guardar_retencion(retencion_data)

            except Exception as e:
                errores.append({"fila": idx + 2, "error": str(e)})

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
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                fecha = datetime.now()
        elif not isinstance(fecha, datetime):
            fecha = datetime.now()
        return fecha.strftime('%Y-%m')

    def _guardar_retencion(self, retencion_data: Dict) -> Optional[Retencion]:
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
        """Generar archivo en formato DIAN."""
        if not retenciones:
            raise ValueError("No hay retenciones para generar")

        lineas = []
        for r in retenciones:
            if r.get('valor_retenido', 0) > 0:
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

        output_file = output_path / f"formato_{formato}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas))

        return output_file

    def generar_reporte_excel(
        self,
        retenciones: List[Dict],
        output_path: Path,
        separar_por_tipo: bool = True
    ):
        """Generar reportes en Excel."""
        if not retenciones:
            raise ValueError("No hay retenciones para reportar")

        excel_gen = ExcelGenerator(output_dir=output_path)

        if separar_por_tipo:
            return excel_gen.generar_reporte_por_tipo(retenciones)

        return excel_gen.generar_reporte_retenciones(retenciones)

    def obtener_resumen(self, retenciones: List[Dict]) -> Dict:
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
        if not self.db:
            return []

        retenciones = self.db.query(Retencion).filter(
            Retencion.periodo == periodo
        ).all()

        return [r.to_dict() for r in retenciones]