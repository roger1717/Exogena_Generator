
# ============================================================================
# MODELS/MAPPING_RULE.PY
# OBJETIVO: Definir el modelo de datos para las reglas de mapeo PUC → Concepto Exógena.
#           Hereda de Base para que SQLAlchemy pueda mapearlo a una tabla en PostgreSQL.
#           Cada instancia representa una regla que asocia una cuenta contable
#           (PUC) con un formato y concepto de información exógena.
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class MappingRule(Base):
    __tablename__ = "mapping_rules"

    id = Column(Integer, primary_key=True, index=True)
    puc_code = Column(String(20), unique=True, index=True, nullable=False)
    puc_name = Column(String(255), nullable=True)
    exogena_format = Column(String(10), nullable=False)
    exogena_concept = Column(String(10), nullable=False)
    exogena_concept_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    __tablename__ = "mapping_rules"
    
    # ID único para cada regla
    id = Column(Integer, primary_key=True, index=True)
    
    # Código PUC - debe ser único para evitar duplicados
    puc_code = Column(String(20), unique=True, index=True, nullable=False)
    
    # Nombre descriptivo del PUC (opcional pero útil)
    puc_name = Column(String(255), nullable=True)
    
    # Formato de exógena (1001, 1003, etc.)
    exogena_format = Column(String(10), nullable=False)
    
    # Concepto específico dentro del formato
    exogena_concept = Column(String(10), nullable=False)
    
    # Nombre descriptivo del concepto (opcional)
    exogena_concept_name = Column(String(255), nullable=True)
    
    # Timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        """Representación legible del objeto para debugging."""
        return f"<MappingRule(puc_code='{self.puc_code}', concept='{self.exogena_concept}')>"