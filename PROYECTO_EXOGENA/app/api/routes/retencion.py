#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rutas para Retenciones en la Fuente

Endpoints para procesar, consultar y generar reportes de retenciones.

"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List

from app.core.database import get_db
from app.services.retencion_service import RetencionService
from app.schemas.retencion import (
    RetencionResponse,
    RetencionListResponse,
    RetencionProcesamientoResult,
    RetencionResumenPorConcepto,
    RetencionResumenPorPeriodo
)
from app.core.config import settings

router = APIRouter(
    prefix="/api/retenciones",
    tags=["Retenciones"],
    responses={404: {"description": "No encontrado"}}
)

# Directorio para archivos temporales
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/procesar", response_model=RetencionProcesamientoResult)
async def procesar_retenciones(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Procesar un archivo Excel con retenciones
    
    - **file**: Archivo Excel con las retenciones
    - Retorna: Resumen del procesamiento
    """
    # Validar extensión
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser Excel (.xlsx o .xls)"
        )
    
    # Guardar archivo temporal
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Procesar
        service = RetencionService(db)
        resultado = service.procesar_desde_excel(file_path)
        
        # Limpiar archivo temporal en background
        background_tasks.add_task(lambda: file_path.unlink(missing_ok=True))
        
        return RetencionProcesamientoResult(
            total_registros=resultado['total_registros'],
            procesados=resultado['procesados'],
            errores=resultado['errores'],
            total_retenido=resultado['total_retenido'],
            detalles=resultado['detalles']
        )
    
    except Exception as e:
        # Limpiar archivo temporal
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=RetencionListResponse)
async def listar_retenciones(
    skip: int = 0,
    limit: int = 100,
    periodo: str = None,
    db: Session = Depends(get_db)
):
    """
    Listar retenciones con paginación
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **periodo**: Filtrar por período (YYYY-MM)
    """
    # TODO: Implementar consulta a BD
    # Por ahora retornamos ejemplo
    return RetencionListResponse(
        total=0,
        items=[],
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/resumen/conceptos", response_model=List[RetencionResumenPorConcepto])
async def resumen_por_concepto(
    periodo: str = None,
    db: Session = Depends(get_db)
):
    """
    Resumen de retenciones agrupadas por concepto
    
    - **periodo**: Período específico (YYYY-MM)
    """
    # TODO: Implementar consulta a BD
    return []


@router.get("/resumen/periodos", response_model=List[RetencionResumenPorPeriodo])
async def resumen_por_periodo(
    db: Session = Depends(get_db)
):
    """
    Resumen de retenciones agrupadas por período
    """
    # TODO: Implementar consulta a BD
    return []


@router.post("/generar-formato")
async def generar_formato_dian(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generar archivo en formato DIAN (1003)
    """
    # TODO: Obtener retenciones de BD
    retenciones = []
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail="No hay retenciones para generar el formato"
        )
    
    service = RetencionService(db)
    output_path = service.generar_formato_dian(retenciones, OUTPUT_DIR)
    
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type="text/plain"
    )


@router.post("/generar-reporte")
async def generar_reporte_excel(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generar reporte en Excel
    """
    # TODO: Obtener retenciones de BD
    retenciones = []
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail="No hay retenciones para generar el reporte"
        )
    
    service = RetencionService(db)
    output_path = service.generar_reporte_excel(retenciones, OUTPUT_DIR)
    
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )