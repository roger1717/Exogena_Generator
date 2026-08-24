"""
Esquemas Pydantic para Retenciones en la Fuente

Define los esquemas de validación y serialización para las retenciones.

"""

from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class RetencionBase(BaseModel):
    """Esquema base con campos comunes de una retención"""
    
    fecha: datetime = Field(..., description="Fecha de la transacción")
    comprobante: str = Field(..., description="Número de comprobante", max_length=50)
    nit_tercero: str = Field(..., description="NIT del tercero", max_length=20)
    nombre_tercero: str = Field(..., description="Nombre del tercero", max_length=255)
    perfil_tributario: Optional[str] = Field(None, description="Perfil tributario", max_length=50)
    
    concepto_contable: str = Field(..., description="Concepto contable", max_length=100)
    concepto_dian: str = Field(..., description="Código DIAN del concepto", max_length=10)
    base_gravable: float = Field(..., description="Base gravable para la retención")
    tarifa: float = Field(..., description="Tarifa aplicada (ej: 0.035 para 3.5%)")
    valor_retenido: float = Field(..., description="Valor retenido")
    cuenta_pasivo: str = Field(..., description="Cuenta PUC del pasivo", max_length=20)
    
    formato_asignado: Optional[str] = Field(None, description="Formato DIAN asignado", max_length=10)
    concepto_exogena: Optional[str] = Field(None, description="Concepto de exógena", max_length=10)
        #Tipo de retención
    tipo_retencion: Optional[str] = Field(None, description="Tipo de retención: renta, iva, ica",max_length=20)

    periodo: Optional[str] = Field(None, description="Período tributario (YYYY-MM)", max_length=7)
    estado: str = Field("procesado", description="Estado de la retención", max_length=20)
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    
    @validator('periodo', always=True)
    def set_periodo(cls, v, values):
        """Asignar período automáticamente desde la fecha"""
        if v is None and 'fecha' in values:
            return values['fecha'].strftime('%Y-%m')
        return v


class RetencionCreate(RetencionBase):
    """Esquema para crear una nueva retención"""
    pass


class RetencionUpdate(BaseModel):
    """Esquema para actualizar una retención existente"""
    estado: Optional[str] = Field(None, max_length=20)
    observaciones: Optional[str] = None
    formato_asignado: Optional[str] = Field(None, max_length=10)
    concepto_exogena: Optional[str] = Field(None, max_length=10)
    tipo_retencion: Optional[str] = Field(None, max_length=20)


class RetencionResponse(RetencionBase):
    """Esquema para responder con datos de retención"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RetencionListResponse(BaseModel):
    """Esquema para listar retenciones con paginación"""
    total: int
    items: List[RetencionResponse]
    page: int
    per_page: int


class RetencionProcesamientoResult(BaseModel):
    """Resultado del procesamiento de retenciones desde archivo"""
    total_registros: int
    procesados: int
    errores: int
    total_retenido: float
    detalles: List[dict]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class RetencionResumenPorConcepto(BaseModel):
    """Resumen de retenciones agrupadas por concepto"""
    concepto_dian: str
    concepto_nombre: str
    cantidad: int
    total_base: float
    total_retenido: float


class RetencionResumenPorPeriodo(BaseModel):
    """Resumen de retenciones agrupadas por período"""
    periodo: str
    total_retenido: float
    cantidad: int

class RetencionResumenPorTipo(BaseModel):
    """Resumen de retenciones agrupadas por tipo"""
    tipo_retencion: str
    tipo_nombre: str
    cantidad: int
    total_retenido: float
    total_base: float


# Esquema para estadísticas completas
class RetencionEstadisticas(BaseModel):
    """Estadísticas completas de retenciones"""
    total_retenciones: int
    total_retenido: float
    total_base: float
    por_tipo: List[RetencionResumenPorTipo]
    por_periodo: List[RetencionResumenPorPeriodo]
    por_concepto: List[RetencionResumenPorConcepto]
    ultimo_periodo: Optional[str]
    periodos_disponibles: List[str]