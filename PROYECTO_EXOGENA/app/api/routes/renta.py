from fastapi import APIRouter, Depends
from app.services.declaracion_renta import calcular_declaracion, generar_reporte

router = APIRouter(prefix="/api/renta", tags=["Declaración de Renta"])


@router.get("/calcular")
async def calcular():
    """Calcular la declaración de renta a partir de los datos en BD"""
    resultado = calcular_declaracion()
    return resultado


@router.get("/reporte")
async def reporte():
    """Obtener la declaración de renta en formato texto"""
    resultado = calcular_declaracion()
    return {
        "resultado": resultado,
        "mensaje": "Consulta exitosa"
    }