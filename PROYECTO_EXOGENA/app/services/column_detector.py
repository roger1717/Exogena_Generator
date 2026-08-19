# ============================================================================
# SERVICES/COLUMN_DETECTOR.PY
# OBJETIVO: Detectar automáticamente las columnas en un CSV basado en
#           similitud de nombres y tipos de datos.
# ============================================================================

import pandas as pd
from typing import Dict, List, Optional, Tuple
import re

class ColumnDetector:
    """
    Detecta automáticamente qué columnas corresponden a cada campo requerido.
    """
    
    # Patrones para buscar en los nombres de columnas
    PATTERNS = {
        'nit': [
            r'nit', r'n\.?i\.?t\.?', r'tercero', r'identificacion', 
            r'cedula', r'ruc', r'documento', r'id'
        ],
        'nombre': [
            r'nombre', r'razon', r'social', r'tercero', r'cliente',
            r'proveedor', r'beneficiario', r'nom'
        ],
        'valor': [
            r'valor', r'monto', r'monto', r'importe', r'cantidad',
            r'debito', r'credito', r'debe', r'haber'
        ],
        'puc': [
            r'cuenta', r'puc', r'codigo', r'code', r'código', 
            r'cta', r'plan'
        ],
        'fecha': [
            r'fecha', r'date', r'dia', r'periodo', r'mes'
        ],
        'concepto': [
            r'concepto', r'descripcion', r'detalle', r'glosa',
            r'observacion', r'nota'
        ]
    }
    
    # Palabras clave para detectar si es débito o crédito
    DEBITO_KEYWORDS = ['debito', 'debe', 'deb', 'cargo']
    CREDITO_KEYWORDS = ['credito', 'haber', 'cred', 'abono']
    
    @classmethod
    def detect_columns(cls, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Detecta automáticamente las columnas en un DataFrame.
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            Diccionario con el mapeo: {campo: nombre_columna}
        """
        columns = df.columns.tolist()
        result = {
            'nit': None,
            'nombre': None,
            'valor': None,
            'puc': None,
            'fecha': None,
            'concepto': None,
            'debito': None,
            'credito': None
        }
        
        # 1. Detectar por coincidencia de patrones
        for column in columns:
            col_lower = column.lower().strip()
            
            # Buscar coincidencias para cada campo
            for field, patterns in cls.PATTERNS.items():
                if result[field] is None:
                    for pattern in patterns:
                        if re.search(pattern, col_lower, re.IGNORECASE):
                            result[field] = column
                            break
            
            # Detectar débito y crédito específicamente
            if result['debito'] is None:
                for keyword in cls.DEBITO_KEYWORDS:
                    if keyword in col_lower:
                        result['debito'] = column
                        break
            
            if result['credito'] is None:
                for keyword in cls.CREDITO_KEYWORDS:
                    if keyword in col_lower:
                        result['credito'] = column
                        break
        
        # 2. Si no se detectó valor, pero hay débito y crédito, calcular
        if result['valor'] is None and result['debito'] is not None and result['credito'] is not None:
            # Verificar que las columnas son numéricas
            if cls._is_numeric_column(df, result['debito']) and cls._is_numeric_column(df, result['credito']):
                result['valor'] = '__calcular_debito_credito__'
        
        # 3. Si no se detectó valor, buscar columna numérica
        if result['valor'] is None:
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if numeric_cols:
                # Usar la primera columna numérica que no sea débito/crédito
                for col in numeric_cols:
                    if col not in [result['debito'], result['credito']]:
                        result['valor'] = col
                        break
                
                # Si todas las numéricas son débito/crédito, usar la primera
                if result['valor'] is None and numeric_cols:
                    result['valor'] = numeric_cols[0]
        
        # 4. Validar que tenemos lo mínimo necesario
        required_fields = ['nit', 'nombre', 'valor', 'puc']
        for field in required_fields:
            if result[field] is None:
                raise ValueError(
                    f"No se pudo detectar la columna para '{field}'. "
                    f"Columnas disponibles: {columns}"
                )
        
        return result
    
    @classmethod
    def _is_numeric_column(cls, df: pd.DataFrame, column: str) -> bool:
        """Verifica si una columna es numérica."""
        try:
            return pd.api.types.is_numeric_dtype(df[column])
        except:
            return False
    
    @classmethod
    def get_required_columns(cls) -> List[str]:
        """Retorna la lista de campos requeridos."""
        return ['nit', 'nombre', 'valor', 'puc']
    
    @classmethod
    def get_column_mapping_description(cls) -> Dict[str, str]:
        """Retorna una descripción de lo que significa cada campo."""
        return {
            'nit': 'Identificación del tercero (NIT, cédula, etc.)',
            'nombre': 'Nombre o razón social del tercero',
            'valor': 'Valor de la transacción (monto)',
            'puc': 'Código de cuenta contable (PUC)',
            'fecha': 'Fecha de la transacción (opcional)',
            'concepto': 'Descripción o concepto (opcional)'
        }