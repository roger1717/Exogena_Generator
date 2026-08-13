# ============================================================================
# SERVICES/CSV_PROCESSOR.PY
# OBJETIVO: Procesar archivos CSV, validar contra reglas de mapeo y
#           generar reportes de errores.
# ============================================================================

import pandas as pd
import uuid
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app.models.mapping_rule import MappingRule
from app.schemas.exogena import ProcessingResult

class CSVProcessor:
    """
    Servicio para procesar archivos CSV de movimientos contables.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el procesador con la sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy para consultar reglas de mapeo
        """
        self.db = db
        self.required_columns = ['nit_tercero', 'nombre_tercero', 'valor', 'codigo_puc']
    
    def process_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], ProcessingResult]:
        """
        Procesa un archivo CSV y retorna los datos procesados y un reporte.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Tuple con (datos_procesados, resultado_del_procesamiento)
        """
        # 1. Cargar el archivo CSV
        df = pd.read_csv(file_path)
        
        # 2. Validar columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas faltantes en el CSV: {missing_cols}")
        
        # 3. Cargar reglas de mapeo desde la base de datos
        rules = self.db.query(MappingRule).all()
        rule_map = {rule.puc_code: rule for rule in rules}
        
        # 4. Procesar cada fila
        processed_data = []
        errors = []
        total_rows = len(df)
        processed_count = 0
        
        for index, row in df.iterrows():
            row_num = index + 2  # +2 porque el índice empieza en 0 y hay encabezado
            
            # Validar campos requeridos
            if pd.isna(row.get('nit_tercero')) or str(row.get('nit_tercero')).strip() == '':
                errors.append({
                    'row': row_num,
                    'error': 'NIT del tercero vacío o inválido'
                })
                continue
            
            if pd.isna(row.get('valor')) or row.get('valor') <= 0:
                errors.append({
                    'row': row_num,
                    'error': f'Valor inválido: {row.get("valor")}'
                })
                continue
            
            # Buscar regla de mapeo para el PUC
            puc_code = str(row.get('codigo_puc')).strip()
            rule = rule_map.get(puc_code)
            
            if not rule:
                errors.append({
                    'row': row_num,
                    'error': f'PUC "{puc_code}" no tiene una regla de mapeo configurada',
                    'data': {
                        'nit': str(row.get('nit_tercero')),
                        'nombre': str(row.get('nombre_tercero')),
                        'valor': float(row.get('valor'))
                    }
                })
                continue
            
            # Crear registro procesado
            processed_row = {
                'nit_tercero': str(row.get('nit_tercero')).strip(),
                'nombre_tercero': str(row.get('nombre_tercero')).strip(),
                'valor': float(row.get('valor')),
                'codigo_puc': puc_code,
                'concepto_asignado': rule.exogena_concept,
                'formato_asignado': rule.exogena_format,
                'estado': 'procesado'
            }
            processed_data.append(processed_row)
            processed_count += 1
        
        # 5. Generar resultado del procesamiento
        result = ProcessingResult(
            filename=Path(file_path).name,
            total_rows=total_rows,
            processed_rows=processed_count,
            error_rows=len(errors),
            errors=errors,
            timestamp=datetime.now()
        )
        
        return processed_data, result
    
    def generate_sample_csv(self) -> str:
        """
        Genera un archivo CSV de ejemplo para pruebas.
        
        Returns:
            Ruta al archivo generado
        """
        sample_data = {
            'nit_tercero': ['900123456-1', '900234567-2', '900345678-3'],
            'nombre_tercero': ['Empresa A', 'Empresa B', 'Empresa C'],
            'valor': [1000000, 2500000, 500000],
            'codigo_puc': ['521005', '511005', '620501']
        }
        
        df = pd.DataFrame(sample_data)
        file_path = Path('uploads') / 'sample_data.csv'
        df.to_csv(file_path, index=False)
        
        return str(file_path)