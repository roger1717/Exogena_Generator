#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Retención en la Fuente

Define el modelo para almacenar retenciones calculadas/procesadas.

Autor: [Tu nombre]
Fecha: 2026-08-22
Versión: 2.0.0
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Text, ForeignKey, Index
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
    __table_args__ = (
        # Índices compuestos para búsquedas frecuentes
        Index('ix_retenciones_periodo_nit', 'periodo', 'nit_tercero'),
        Index('ix_retenciones_fecha_comprobante', 'fecha', 'comprobante'),
        Index('ix_retenciones_tipo_periodo', 'tipo_retencion', 'periodo'),  # 🔵 NUEVO
    )

    # ============================================================================
    # ID
    # ============================================================================
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ============================================================================
    # Datos de la transacción
    # ============================================================================
    
    fecha = Column(DateTime, nullable=False)
    """Fecha de la transacción (factura/comprobante)"""
    
    comprobante = Column(String(50), nullable=False)
    """Número del comprobante contable (ej: AS-1046)"""
    
    nit_tercero = Column(String(20), nullable=False, index=True)
    """NIT del tercero (proveedor/cliente)"""
    
    nombre_tercero = Column(String(255), nullable=False)
    """Nombre del tercero"""
    
    perfil_tributario = Column(String(50), nullable=True)
    """Perfil tributario del tercero (ej: Responsable IVA)"""
    
    # ============================================================================
    # Datos de la retención
    # ============================================================================
    
    concepto_contable = Column(String(100), nullable=False)
    """Concepto contable de la retención (ej: Arrendamientos)"""
    
    concepto_dian = Column(String(10), nullable=False)
    """Código de concepto DIAN para retención (ej: 01, 02, 03)"""
    
    base_gravable = Column(Numeric(15, 2), nullable=False)
    """Base gravable sobre la que se calcula la retención"""
    
    tarifa = Column(Numeric(10, 4), nullable=False)
    """Tarifa aplicada (ej: 0.035 para 3.5%)"""
    
    valor_retenido = Column(Numeric(15, 2), nullable=False)
    """Valor retenido calculado (Base * Tarifa)"""
    
    cuenta_pasivo = Column(String(20), nullable=False)
    """Cuenta PUC del pasivo donde se registra la retención (ej: 236530)"""
    
    # 🔵 NUEVO: Tipo de retención
    tipo_retencion = Column(String(20), nullable=True, default='renta')
    """
    Tipo de retención:
    - renta: ReteFuente
    - iva: ReteIVA
    - ica: ReteICA
    """
    
    # ============================================================================
    # Datos de exógena (relación)
    # ============================================================================
    
    formato_asignado = Column(String(10), nullable=True)
    """Formato de exógena asignado (1001, 1003, etc.)"""
    
    concepto_exogena = Column(String(10), nullable=True)
    """Concepto de exógena asignado (ej: 5025, 5002)"""

    # ============================================================================
    # Metadatos
    # ============================================================================
    
    periodo = Column(String(7), nullable=False, index=True)
    """Período tributario (YYYY-MM)"""
    
    estado = Column(String(20), default="procesado")
    """
    Estado de la retención:
    - procesado: Calculado pero no reportado
    - reportado: Incluido en reporte DIAN
    - error: Error en el procesamiento
    - no_aplica: No aplica retención (tope mínimo)
    """
    
    observaciones = Column(Text, nullable=True)
    """Observaciones adicionales o errores"""
    
    # ============================================================================
    # Auditoría
    # ============================================================================
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """Fecha de creación del registro"""
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    """Fecha de última actualización del registro"""
    
    # ============================================================================
    # Métodos
    # ============================================================================
    
    def __repr__(self) -> str:
        """Representación legible del objeto para debugging"""
        return (
            f"<Retencion("
            f"comprobante='{self.comprobante}', "
            f"nit='{self.nit_tercero}', "
            f"tipo='{self.tipo_retencion}', "
            f"valor={self.valor_retenido}, "
            f"periodo='{self.periodo}'"
            f")>"
        )
    
    def get_valor_float(self) -> float:
        """Obtener el valor retenido como float"""
        return float(self.valor_retenido)
    
    def get_base_float(self) -> float:
        """Obtener la base gravable como float"""
        return float(self.base_gravable)
    
    def get_tarifa_float(self) -> float:
        """Obtener la tarifa como float"""
        return float(self.tarifa)
    
    def get_tipo_nombre(self) -> str:
        """Obtener el nombre descriptivo del tipo de retención"""
        tipos = {
            "renta": "ReteFuente",
            "iva": "ReteIVA",
            "ica": "ReteICA",
        }
        return tipos.get(self.tipo_retencion, self.tipo_retencion or "Desconocido")
    
    def to_dict(self) -> dict:
        """
        Convertir el modelo a diccionario para respuestas API
        
        Returns:
            Diccionario con todos los campos
        """
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "comprobante": self.comprobante,
            "nit_tercero": self.nit_tercero,
            "nombre_tercero": self.nombre_tercero,
            "perfil_tributario": self.perfil_tributario,
            "concepto_contable": self.concepto_contable,
            "concepto_dian": self.concepto_dian,
            "base_gravable": float(self.base_gravable),
            "tarifa": float(self.tarifa),
            "valor_retenido": float(self.valor_retenido),
            "cuenta_pasivo": self.cuenta_pasivo,
            "tipo_retencion": self.tipo_retencion,  # 🔵 NUEVO
            "formato_asignado": self.formato_asignado,
            "concepto_exogena": self.concepto_exogena,
            "periodo": self.periodo,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }