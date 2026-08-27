# ============================================================================
# SCHEMAS/EXOGENA.PY
# OBJETIVO: Definir los esquemas Pydantic para el procesamiento de exógena.
#           Incluye validación de archivos CSV, reportes de procesamiento
#           y respuestas de la API.
# ============================================================================

# app/schemas/exogena.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class CSVRow(BaseModel):
    nit_tercero: str = Field(..., description="NIT del tercero")
    nombre_tercero: str = Field(..., description="Nombre del tercero")
    valor: float = Field(..., description="Valor de la transacción")
    codigo_puc: str = Field(..., description="Código PUC de la cuenta contable")
    concepto_asignado: Optional[str] = Field(None, description="Concepto de exógena asignado")
    formato_asignado: Optional[str] = Field(None, description="Formato de exógena asignado")
    estado: str = Field("pendiente", description="Estado del registro: pendiente, procesado, error")

class ProcessingResult(BaseModel):
    filename: str = Field(..., description="Nombre del archivo procesado")
    total_rows: int = Field(..., description="Total de filas procesadas")
    processed_rows: int = Field(..., description="Filas procesadas exitosamente")
    error_rows: int = Field(..., description="Filas con errores")
    errors: List[Dict[str, Any]] = Field([], description="Lista de errores encontrados")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del procesamiento")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class CSVUploadResponse(BaseModel):
    message: str
    file_id: str
    json_path: str = Field(..., description="Ruta relativa del archivo JSON generado")
    excel_path: str = Field(..., description="Ruta relativa del archivo Excel generado")
    result: ProcessingResult
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )