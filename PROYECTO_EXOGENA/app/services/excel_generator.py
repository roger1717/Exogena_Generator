#!/usr/bin/env python

"""
Generador de archivos Excel para Retenciones en la Fuente

Autor: [Tu nombre]
Fecha: 2026-08-22
Versión: 2.0.0
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ExcelGenerator:
    
    TIPO_A_NOMBRE = {
        "renta": "ReteFuente",
        "iva": "ReteIVA",
        "ica": "ReteICA",
    }
    
    def __init__(self, output_dir: Path = Path("outputs/excel")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_reporte_retenciones(
        self,
        retenciones: List[Dict],
        periodo: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> Path:
        """Generar reporte de retenciones en Excel"""
        
        if not retenciones:
            raise ValueError("No hay retenciones para generar")
        
        if tipo is None and retenciones:
            tipo = retenciones[0].get('tipo_retencion', 'renta')
        
        nombre_tipo = self.TIPO_A_NOMBRE.get(tipo, "Retenciones")
        
        if periodo:
            filename = f"1003-{nombre_tipo}-{periodo}.xlsx"
        else:
            filename = f"1003-{nombre_tipo}-{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        file_path = self.output_dir / filename
        wb = Workbook()
        
        # === HOJA 1: Detalle ===
        ws_detalle = wb.active
        ws_detalle.title = "Detalle"
        
        df = pd.DataFrame(retenciones)
        
        columnas = [
            ('fecha', 'Fecha'),
            ('comprobante', 'Comprobante'),
            ('nit_tercero', 'NIT'),
            ('nombre_tercero', 'Nombre Tercero'),
            ('concepto_contable', 'Concepto Contable'),
            ('concepto_dian', 'Código DIAN'),
            ('base_gravable', 'Base Gravable'),
            ('tarifa', 'Tarifa'),
            ('valor_retenido', 'Valor Retenido'),
            ('cuenta_pasivo', 'Cuenta Pasivo'),
            ('periodo', 'Período'),
            ('tipo_retencion', 'Tipo'),
        ]
        
        columnas_existentes = [(orig, dest) for orig, dest in columnas if orig in df.columns]
        df_detalle = df[[orig for orig, _ in columnas_existentes]].copy()
        df_detalle.columns = [dest for _, dest in columnas_existentes]
        
        for col_idx, col_name in enumerate(df_detalle.columns, 1):
            cell = ws_detalle.cell(row=1, column=col_idx, value=col_name)
            cell.font = Font(bold=True, color="000000")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        
        for r_idx, row in enumerate(df_detalle.itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                cell = ws_detalle.cell(row=r_idx, column=c_idx, value=value)
                if c_idx in [7, 9]:
                    cell.number_format = '#,##0.00'
                if c_idx == 8:
                    cell.number_format = '0.00%'
        
        for col in ws_detalle.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_detalle.column_dimensions[column].width = adjusted_width
        
        # === HOJA 2: Resumen por Concepto ===
        ws_resumen = wb.create_sheet("Resumen por Concepto")
        
        if 'concepto_dian' in df.columns:
            from app.core.constants import CONCEPTOS_RETENCION_DIAN
            
            df_resumen = df.groupby('concepto_dian').agg({
                'valor_retenido': ['count', 'sum'],
                'base_gravable': 'sum'
            }).round(2)
            
            df_resumen.columns = ['Cantidad', 'Total Retenido', 'Total Base']
            df_resumen = df_resumen.reset_index()
            df_resumen['Concepto'] = df_resumen['concepto_dian'].map(
                lambda x: CONCEPTOS_RETENCION_DIAN.get(str(x), x)
            )
            df_resumen = df_resumen[['concepto_dian', 'Concepto', 'Cantidad', 'Total Base', 'Total Retenido']]
            
            for col_idx, col_name in enumerate(df_resumen.columns, 1):
                cell = ws_resumen.cell(row=1, column=col_idx, value=col_name)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
            
            for r_idx, row in enumerate(df_resumen.itertuples(index=False), 2):
                for c_idx, value in enumerate(row, 1):
                    cell = ws_resumen.cell(row=r_idx, column=c_idx, value=value)
                    if c_idx in [4, 5]:
                        cell.number_format = '#,##0.00'
            
            for col in ws_resumen.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                ws_resumen.column_dimensions[column].width = adjusted_width
        
        # === HOJA 3: Resumen por Período ===
        ws_periodo = wb.create_sheet("Resumen por Período")
        
        if 'periodo' in df.columns:
            df_periodo = df.groupby('periodo').agg({
                'valor_retenido': ['count', 'sum']
            }).round(2)
            df_periodo.columns = ['Cantidad', 'Total Retenido']
            df_periodo = df_periodo.reset_index()
            
            for col_idx, col_name in enumerate(df_periodo.columns, 1):
                cell = ws_periodo.cell(row=1, column=col_idx, value=col_name)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="ED7D31", end_color="ED7D31", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
            
            for r_idx, row in enumerate(df_periodo.itertuples(index=False), 2):
                for c_idx, value in enumerate(row, 1):
                    cell = ws_periodo.cell(row=r_idx, column=c_idx, value=value)
                    if c_idx == 3:
                        cell.number_format = '#,##0.00'
            
            for col in ws_periodo.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                ws_periodo.column_dimensions[column].width = adjusted_width
        
        # === HOJA 4: Resumen por Tipo ===
        ws_tipo = wb.create_sheet("Resumen por Tipo")
        
        if 'tipo_retencion' in df.columns:
            df_tipo = df.groupby('tipo_retencion').agg({
                'valor_retenido': ['count', 'sum']
            }).round(2)
            df_tipo.columns = ['Cantidad', 'Total Retenido']
            df_tipo = df_tipo.reset_index()
            df_tipo['Tipo'] = df_tipo['tipo_retencion'].map(
                lambda x: self.TIPO_A_NOMBRE.get(x, x)
            )
            df_tipo = df_tipo[['Tipo', 'Cantidad', 'Total Retenido']]
            
            for col_idx, col_name in enumerate(df_tipo.columns, 1):
                cell = ws_tipo.cell(row=1, column=col_idx, value=col_name)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
                cell.alignment = Alignment(horizontal='center')
            
            for r_idx, row in enumerate(df_tipo.itertuples(index=False), 2):
                for c_idx, value in enumerate(row, 1):
                    cell = ws_tipo.cell(row=r_idx, column=c_idx, value=value)
                    if c_idx == 3:
                        cell.number_format = '#,##0.00'
            
            for col in ws_tipo.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                ws_tipo.column_dimensions[column].width = adjusted_width
        
        wb.save(file_path)
        logger.info(f"📊 Excel generado: {file_path}")
        
        return file_path
    
    def generar_reporte_por_tipo(
        self,
        retenciones: List[Dict],
        periodo: Optional[str] = None
    ) -> Dict[str, Path]:
        """Generar reportes separados por tipo de retención"""
        if not retenciones:
            return {}
        
        retenciones_por_tipo = {}
        for r in retenciones:
            tipo = r.get('tipo_retencion', 'renta')
            if tipo not in retenciones_por_tipo:
                retenciones_por_tipo[tipo] = []
            retenciones_por_tipo[tipo].append(r)
        
        archivos_generados = {}
        
        for tipo, retenciones_tipo in retenciones_por_tipo.items():
            archivo = self.generar_reporte_retenciones(
                retenciones=retenciones_tipo,
                periodo=periodo,
                tipo=tipo
            )
            archivos_generados[tipo] = archivo
        
        return archivos_generados