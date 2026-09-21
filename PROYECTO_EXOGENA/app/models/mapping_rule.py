# ============================================================================
# MODELS/MAPPING_RULE.PY
# OBJETIVO: Definir el modelo de datos para las reglas de mapeo PUC → Concepto Exógena.
#           Hereda de Base para que SQLAlchemy pueda mapearlo a una tabla.
#           Cada instancia representa una regla que asocia una cuenta contable
#           (PUC) con un formato y concepto de información exógena.
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class MappingRule(Base):
    __tablename__ = "mapping_rules"

    id = Column(Integer, primary_key=True, index=True)

    # ========================================================================
    # Datos de cuenta contable (PUC)
    # ========================================================================

    puc_code = Column(String(20), unique=True, index=True, nullable=False)
    """Código de cuenta PUC (ej: 236530)"""

    puc_name = Column(String(255), nullable=True)
    """Nombre descriptivo de la cuenta (ej: Retencion Arrendamientos 3.5%)"""

    # ========================================================================
    # Datos de exógena
    # ========================================================================

    exogena_format = Column(String(10), nullable=False)
    """Formato de exógena (1001, 1007, 1008, 1009)"""

    exogena_concept = Column(String(10), nullable=False)
    """Código de concepto para exógena (ej: 5025, 5002)"""

    exogena_concept_name = Column(String(255), nullable=True)
    """Nombre descriptivo del concepto de exógena"""

    # ========================================================================
    # Datos de retención en la fuente
    # ========================================================================

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

    calcula_base_sobre = Column(String(10), nullable=True, default="valor")
    """Sobre qué se calcula la base: 'valor', 'total', 'iva'"""

    cliente = Column(String(50), nullable=True, index=True)
    """Cliente específico para tarifas ICA (ALION, HOLCIM, etc.)"""

    # ========================================================================
    # NUEVO: Tipo de regla (retención vs gasto vs exógena)
    # ========================================================================

    tipo_regla = Column(
        String(20),
        nullable=True,
        default="retencion",
        index=True,
    )
    """
    Tipo de regla según la clase de cuenta PUC:
      - 'retencion': cuenta 2365xx / 2368xx / 236535-537 (retención en la fuente)
      - 'gasto': cuenta 5xxxxx (gasto asociado a retención, informativo)
      - 'exogena': cuenta 1xxxxx, 2xxxxx, 4xxxxx (exógena sin retención)
    """

    # ========================================================================
    # Estado y auditoría
    # ========================================================================

    activo = Column(Boolean, nullable=True, default=True)
    """¿La regla está activa y debe ser considerada?"""

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ========================================================================
    # MÉTODOS DE REPRESENTACIÓN
    # ========================================================================

    def __repr__(self) -> str:
        """Representación legible del objeto para debugging"""
        return (
            f"<MappingRule("
            f"puc_code='{self.puc_code}', "
            f"tipo_regla='{self.tipo_regla}', "
            f"tipo_retencion='{self.tipo_retencion}', "
            f"concepto_retencion='{self.concepto_retencion}', "
            f"activo={self.activo}"
            f")>"
        )

    # ========================================================================
    # MÉTODOS DE CLASIFICACIÓN
    # ========================================================================

    def es_retencion(self) -> bool:
        """
        Determina si esta regla aplica para retención en la fuente.
        Requiere:
          - tipo_regla == 'retencion'
          - activo == True
          - concepto_retencion no nulo
        """
        return (
            self.activo is True
            and self.tipo_regla == "retencion"
            and self.concepto_retencion is not None
        )

    def es_regla_gasto(self) -> bool:
        """Verifica si la regla es de tipo gasto (cuenta 5xxxxx)."""
        return self.tipo_regla == "gasto"

    def es_regla_exogena(self) -> bool:
        """Verifica si la regla es solo de exógena."""
        return self.tipo_regla == "exogena"

    def es_cuenta_puc_retencion(self) -> bool:
        """
        Verifica si el PUC es una cuenta de retención según su prefijo.
        Útil como defensa en profundidad contra datos mal clasificados.
        """
        if not self.puc_code:
            return False
        return self.puc_code.startswith(("2365", "2368"))

    # ========================================================================
    # MÉTODOS DE CONVERSIÓN
    # ========================================================================

    def get_tarifa_float(self) -> float:
        """Obtener la tarifa como float (ej: 0.035)."""
        return float(self.tarifa_retencion) if self.tarifa_retencion else 0.0

    def get_tope_float(self) -> float:
        """Obtener el tope mínimo como float (en COP)."""
        return float(self.tope_minimo) if self.tope_minimo else 0.0

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario para respuestas API."""
        return {
            "id": self.id,
            "puc_code": self.puc_code,
            "puc_name": self.puc_name,
            "exogena_format": self.exogena_format,
            "exogena_concept": self.exogena_concept,
            "exogena_concept_name": self.exogena_concept_name,
            "concepto_retencion": self.concepto_retencion,
            "tarifa_retencion": float(self.tarifa_retencion) if self.tarifa_retencion else None,
            "tope_minimo": float(self.tope_minimo) if self.tope_minimo else None,
            "aplica_iva": self.aplica_iva,
            "tipo_retencion": self.tipo_retencion,
            "tipo_regla": self.tipo_regla,
            "calcula_base_sobre": self.calcula_base_sobre,
            "cliente": self.cliente,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }