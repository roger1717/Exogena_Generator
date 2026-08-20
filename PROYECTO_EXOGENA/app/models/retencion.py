

"""
Modelo de Retención en la Fuente

Define el modelo para almacenar retenciones calculadas/procesadas.


"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Retencion(Base):
    """
    Modelo de Retención en la Fuente
    
    Almacena las retenciones procesadas desde el auxiliar contable
    o desde archivos Excel.
    """
    __tablename__ = "retenciones"
    
    # ID único
    id = Column(Integer, primary_key=True, index=True)
    
    # Datos de la transacción
    fecha = Column(DateTime, nullable=False)
    comprobante = Column(String(50), nullable=False)
    nit_tercero = Column(String(20), nullable=False, index=True)
    nombre_tercero = Column(String(255), nullable=False)
    perfil_tributario = Column(String(50), nullable=True)
    
    # Datos de la retención
    concepto_contable = Column(String(100), nullable=False)
    concepto_dian = Column(String(10), nullable=False)
    base_gravable = Column(Numeric(15, 2), nullable=False)
    tarifa = Column(Numeric(10, 4), nullable=False)
    valor_retenido = Column(Numeric(15, 2), nullable=False)
    cuenta_pasivo = Column(String(20), nullable=False)
    
    # Datos de exógena (relación)
    formato_asignado = Column(String(10), nullable=True)  # 1001, 1003, etc.
    concepto_exogena = Column(String(10), nullable=True)  # Concepto para exógena
    
    # Metadatos
    periodo = Column(String(7), nullable=False)  # YYYY-MM
    estado = Column(String(20), default="procesado")  # procesado, reportado, error
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Retencion(comprobante='{self.comprobante}', valor={self.valor_retenido})>"