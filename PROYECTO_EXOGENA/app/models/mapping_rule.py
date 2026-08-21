
# ============================================================================
# MODELS/MAPPING_RULE.PY
# OBJETIVO: Definir el modelo de datos para las reglas de mapeo PUC → Concepto Exógena.
#           Hereda de Base para que SQLAlchemy pueda mapearlo a una tabla en PostgreSQL.
#           Cada instancia representa una regla que asocia una cuenta contable
#           (PUC) con un formato y concepto de información exógena.
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime,Numeric,Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class MappingRule(Base):
    __tablename__ = "mapping_rules"

    id = Column(Integer, primary_key=True, index=True)
    #Datos de cuenta contable (puc)
    puc_code = Column(String(20), unique=True, index=True, nullable=False)
    """Código de cuenta PUC (ej: 236530)"""
    
    puc_name = Column(String(255), nullable=True)
    """Nombre descriptivo de la cuenta (ej: Retencion Arrendamientos 3.5%)"""
    #Datos de exogena
    exogena_format = Column(String(10), nullable=False)
    """Formato de exógena (1001, 1007, 1008, 1009)"""
    
    exogena_concept = Column(String(10), nullable=False)
    """Código de concepto para exógena (ej: 5025, 5002)"""
    
    exogena_concept_name = Column(String(255), nullable=True)
    """Nombre descriptivo del concepto de exógena"""
    #Datos de retencion en la fuente
    concepto_retencion = Column(String(10), nullable=True)
    """Código de concepto DIAN para retención (ej: 01, 02, 03)"""
    tarifa_retencion = Column(Numeric(10, 4), nullable=True)
    """Tarifa de retención (ej: 0.035 para 3.5%)"""
    tope_minimo = Column(Numeric(15, 2), nullable=True)
    """Tope mínimo para aplicar retención en COP (ej: 100000)"""
    aplica_iva = Column(Boolean, nullable=True, default=False)
    """¿Aplica IVA en la base de cálculo de retención?"""
    tipo_retencion = Column(String(20), nullable=True)
    """Tipo de retención: renta, iva, ica"""
    activo = Column(Boolean, nullable=True, default=True)
    """¿La regla está activa y debe ser considerada?"""
    #Datos de auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    def __repr__(self) -> str:
        """Representación legible del objeto para debugging"""
        return (
            f"<MappingRule("
            f"puc_code='{self.puc_code}', "
            f"exogena_concept='{self.exogena_concept}', "
            f"concepto_retencion='{self.concepto_retencion}', "
            f"activo={self.activo}"
            f")>"
        )
    
    def es_retencion(self) -> bool:
        """
        Determinar si esta regla aplica para retención
        
        Returns:
            True si tiene concepto_retencion y está activa
        """
        return self.activo and self.concepto_retencion is not None
    
    def get_tarifa_float(self) -> float:
        """
        Obtener la tarifa como float
        
        Returns:
            Tarifa como float (ej: 0.035)
        """
        return float(self.tarifa_retencion) if self.tarifa_retencion else 0.0
    
    def get_tope_float(self) -> float:
        """
        Obtener el tope mínimo como float
        
        Returns:
            Tope mínimo como float
        """
        return float(self.tope_minimo) if self.tope_minimo else 0.0