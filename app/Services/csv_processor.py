# ============================================================================
# SERVICES/CSV_PROCESSOR.PY
# OBJETIVO: Procesar archivos CSV con detección automática de columnas
# ============================================================================

import pandas as pd
import json
from typing import Dict, List, Any, Tuple, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app.models.mapping_rule import MappingRule
from app.schemas.exogena import ProcessingResult
from app.services.column_detector import ColumnDetector

class CSVProcessor:
    """
    Servicio para procesar archivos CSV con detección automática de columnas.
    """
    
    def __init__(self, db: Session, column_mapping: Optional[Dict[str, str]] = None):
        """
        Inicializa el procesador.
        
        Args:
            db: Sesión de base de datos
            column_mapping: Mapeo manual de columnas (opcional)
        """
        self.db = db
        self.column_mapping = column_mapping
    
    def process_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], ProcessingResult]:
        """Procesa un archivo CSV con detección automática de columnas."""
        
        # 1. Cargar el archivo CSV
        df = self._load_csv(file_path)
        
        # 2. Detectar columnas
        if self.column_mapping:
            # Usar mapeo manual si se proporcionó
            column_map = self.column_mapping
        else:
            # Detectar automáticamente
            column_map = ColumnDetector.detect_columns(df)
        
        # 3. Normalizar datos
        df_normalized = self._normalize_dataframe(df, column_map)
        
        # 4. Cargar reglas de mapeo
        rules = self.db.query(MappingRule).all()
        rule_map = {rule.puc_code: rule for rule in rules}
        
        # 5. Procesar filas
        processed_data, errors = self._process_rows(df_normalized, rule_map)
        
        # 6. Generar resultado
        result = ProcessingResult(
            filename=Path(file_path).name,
            total_rows=len(df_normalized),
            processed_rows=len(processed_data),
            error_rows=len(errors),
            errors=errors,
            timestamp=datetime.now()
        )
        
        return processed_data, result
    
    def _load_csv(self, file_path: str) -> pd.DataFrame:
        """Carga un CSV con diferentes codificaciones."""
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                # Normalizar nombres de columnas
                df.columns = df.columns.str.strip()
                return df
            except:
                continue
        
        raise ValueError(f"No se pudo leer el archivo {file_path} con ninguna codificación")
    
    def _normalize_dataframe(self, df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
        """Normaliza el DataFrame usando el mapeo de columnas."""
        df_normalized = pd.DataFrame()
        
        # Mapear NIT
        if column_map.get('nit'):
            df_normalized['nit_tercero'] = df[column_map['nit']].astype(str).str.strip()
        
        # Mapear nombre
        if column_map.get('nombre'):
            df_normalized['nombre_tercero'] = df[column_map['nombre']].astype(str).str.strip()
        
        # Mapear PUC
        if column_map.get('puc'):
            df_normalized['codigo_puc'] = df[column_map['puc']].astype(str).str.strip()
        
        # Mapear valor (puede ser directo o calculado)
        if column_map.get('valor') == '__calcular_debito_credito__':
            # Calcular desde débito y crédito
            debito_col = column_map.get('debito')
            credito_col = column_map.get('credito')
            
            if debito_col and credito_col:
                df_normalized['valor'] = (
                    pd.to_numeric(df[debito_col], errors='coerce').fillna(0) +
                    pd.to_numeric(df[credito_col], errors='coerce').fillna(0)
                )
            else:
                df_normalized['valor'] = 0
        elif column_map.get('valor'):
            # Usar columna directa
            df_normalized['valor'] = pd.to_numeric(df[column_map['valor']], errors='coerce').fillna(0)
        else:
            df_normalized['valor'] = 0
        
        # Mapear fecha (opcional)
        if column_map.get('fecha'):
            try:
                df_normalized['fecha'] = pd.to_datetime(df[column_map['fecha']])
            except:
                df_normalized['fecha'] = None
        
        # Mapear concepto (opcional)
        if column_map.get('concepto'):
            df_normalized['concepto'] = df[column_map['concepto']].astype(str)
        
        # Limpiar datos
        df_normalized = df_normalized.dropna(subset=['nit_tercero', 'codigo_puc'])
        df_normalized = df_normalized[df_normalized['nit_tercero'] != '']
        df_normalized = df_normalized[df_normalized['nit_tercero'] != 'nan']
        df_normalized = df_normalized[df_normalized['codigo_puc'] != '']
        df_normalized = df_normalized[df_normalized['codigo_puc'] != 'nan']
        df_normalized = df_normalized[df_normalized['valor'] != 0]
        
        return df_normalized
    
    def _process_rows(self, df: pd.DataFrame, rule_map: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """Procesa cada fila del DataFrame."""
        processed_data = []
        errors = []
        
        for index, row in df.iterrows():
            row_num = index + 2
            
            nit = str(row.get('nit_tercero', '')).strip()
            nombre = str(row.get('nombre_tercero', '')).strip()
            valor = float(row.get('valor', 0))
            puc_code = str(row.get('codigo_puc', '')).strip()
            
            # Validaciones
            if not nit or nit == 'nan':
                errors.append({'row': row_num, 'error': 'NIT vacío o inválido'})
                continue
            
            if valor == 0:
                errors.append({'row': row_num, 'error': 'Valor cero (no se reporta)'})
                continue
            
            if not puc_code or puc_code == 'nan':
                errors.append({
                    'row': row_num,
                    'error': 'Código PUC vacío',
                    'data': {'nit': nit, 'nombre': nombre, 'valor': valor}
                })
                continue
            
            # Buscar regla de mapeo
            rule = rule_map.get(puc_code)
            if not rule:
                errors.append({
                    'row': row_num,
                    'error': f'PUC "{puc_code}" sin regla de mapeo',
                    'data': {'nit': nit, 'nombre': nombre, 'valor': valor}
                })
                continue
            
            # Crear registro procesado
            processed_data.append({
                'nit_tercero': nit,
                'nombre_tercero': nombre,
                'valor': valor,
                'codigo_puc': puc_code,
                'concepto_asignado': rule.exogena_concept,
                'formato_asignado': rule.exogena_format,
                'estado': 'procesado'
            })
        
        return processed_data, errors
    
    def generate_sample_csv(self) -> str:
        """Genera un archivo CSV de ejemplo."""
        sample_data = {
            'nit_tercero': ['900123456-1', '900234567-2', '900345678-3'],
            'nombre_tercero': ['Empresa A', 'Empresa B', 'Empresa C'],
            'valor': [1000000, 2500000, 500000],
            'codigo_puc': ['512010', '511005', '413505']
        }
        
        df = pd.DataFrame(sample_data)
        file_path = Path('uploads') / 'sample_data.csv'
        file_path.parent.mkdir(exist_ok=True)
        df.to_csv(file_path, index=False)
        
        return str(file_path)
    
    def get_column_suggestions(self, file_path: str) -> Dict[str, Any]:
        """
        Analiza un CSV y sugiere qué columnas usar para cada campo.
        Útil para dar feedback al usuario.
        """
        df = self._load_csv(file_path)
        detection = ColumnDetector.detect_columns(df)
        
        return {
            'columns_available': df.columns.tolist(),
            'detected_mapping': detection,
            'description': ColumnDetector.get_column_mapping_description()
        }