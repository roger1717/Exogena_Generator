# ============================================================================
# SCHEMAS/MAPPING.PY
# OBJETIVO: Definir los esquemas Pydantic para validación y serialización
#           de las reglas de mapeo.
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class MappingRuleBase(BaseModel):
    """
    Esquema base con los campos comunes de una regla de mapeo.
    """
    puc_code: str = Field(..., description="Código de cuenta PUC", max_length=20)
    puc_name: Optional[str] = Field(None, description="Nombre de la cuenta", max_length=255)
    exogena_format: str = Field(..., description="Formato de exógena", max_length=10)
    exogena_concept: str = Field(..., description="Concepto de exógena", max_length=10)
    exogena_concept_name: Optional[str] = Field(None, description="Nombre del concepto", max_length=255)

class MappingRuleCreate(MappingRuleBase):
    """
    Esquema para crear una nueva regla.
    Todos los campos son requeridos (excepto los opcionales).
    """
    pass

class MappingRuleUpdate(BaseModel):
    """
    Esquema para actualizar una regla existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    puc_code: Optional[str] = Field(None, max_length=20)
    puc_name: Optional[str] = Field(None, max_length=255)
    exogena_format: Optional[str] = Field(None, max_length=10)
    exogena_concept: Optional[str] = Field(None, max_length=10)
    exogena_concept_name: Optional[str] = Field(None, max_length=255)

class MappingRuleResponse(MappingRuleBase):
    """
    Esquema para retornar una regla desde la API.
    Incluye el ID y los timestamps automáticos.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Configuración para que Pydantic pueda leer objetos SQLAlchemy
    model_config = ConfigDict(from_attributes=True)