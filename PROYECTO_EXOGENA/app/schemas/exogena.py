# ============================================================================
# SCHEMAS/EXOGENA.PY
# OBJETIVO: Definir los esquemas Pydantic para el procesamiento de exógena.
#           Incluye validación de archivos CSV, reportes de procesamiento
#           y respuestas de la API.
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class CSVRow(BaseModel):
    """
    Representa una fila del archivo CSV procesado.
    """
    nit_tercero: str = Field(..., description="NIT del tercero")
    nombre_tercero: str = Field(..., description="Nombre del tercero")
    valor: float = Field(..., description="Valor de la transacción")
    codigo_puc: str = Field(..., description="Código PUC de la cuenta contable")
    concepto_asignado: Optional[str] = Field(None, description="Concepto de exógena asignado")
    formato_asignado: Optional[str] = Field(None, description="Formato de exógena asignado")
    estado: str = Field("pendiente", description="Estado del registro: pendiente, procesado, error")

class ProcessingResult(BaseModel):
    """
    Resultado del procesamiento de un archivo CSV.
    """
    filename: str = Field(..., description="Nombre del archivo procesado")
    total_rows: int = Field(..., description="Total de filas procesadas")
    processed_rows: int = Field(..., description="Filas procesadas exitosamente")
    error_rows: int = Field(..., description="Filas con errores")
    errors: List[Dict[str, Any]] = Field([], description="Lista de errores encontrados")
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del procesamiento")
    
    model_config = ConfigDict(
        from_attributes=True,
        # Esto asegura que datetime se serialice como string ISO
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class CSVUploadResponse(BaseModel):
    """
    Respuesta al subir un archivo CSV.
    """
    message: str
    file_id: str
    result: ProcessingResult
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )