#app/api/routes.py

"""
Rutas para Retenciones en la Fuente

Endpoints para procesar, consultar y generar reportes de retenciones.

"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pathlib import Path
from typing import List, Optional

from app.core.database import get_db
from app.services.retencion_service import RetencionService
from app.services.retencion_csv_processor import RetencionCSVProcessor
from app.services.ecxel_generator import ExcelGenerator
from app.services.xml_generator import XMLGenerator
from app.models.retencion import Retencion
from app.schemas.retencion import (
    RetencionResponse,
    RetencionListResponse,
    RetencionProcesamientoResult,
    RetencionResumenPorConcepto,
    RetencionResumenPorPeriodo
)
from app.core.config import settings
from app.core.constants import CONCEPTOS_RETENCION_DIAN

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


# ============================================================================
# ENDPOINT PRINCIPAL: PROCESAR ARCHIVO
# ============================================================================

@router.post("/procesar")
async def procesar_retenciones(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Procesar un archivo de retenciones (Excel o CSV)
    
    - **file**: Archivo Excel (.xlsx, .xls) o CSV (.csv) con las retenciones
    - Retorna: Resumen del procesamiento con archivos generados
    
    **Formatos soportados:**
    
    **Excel (Formato específico de retenciones):**
    - Columnas requeridas: Fecha_Transaccion, Comprobante, NIT_Tercero, 
      Razon_Social, Concepto_Contable, Base_Gravable, 
      Porcentaje_ReteFuente, Valor_Retenido, Cuenta_Pasivo
    
    **CSV (Auxiliar contable):**
    - Columnas requeridas: Fecha, Asiento, Cuenta, NIT_Tercero, 
      Razon_Social, (Debito o Credito)
    - Las cuentas 2365xx se extraen automáticamente como retenciones
    """
    # Validar extensión
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser Excel (.xlsx, .xls) o CSV (.csv)"
        )
    
    # Guardar archivo temporal
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Detectar tipo de archivo
        extension = file.filename.split('.')[-1].lower()
        
        if extension == 'csv':
            # ================================================================
            # PROCESAR CSV (Auxiliar contable)
            # ================================================================
            processor = RetencionCSVProcessor(db)
            retenciones, resumen = processor.procesar_archivo(file_path)
            
            # Generar archivos si hay retenciones
            archivos_generados = {}
            if retenciones:
                # Generar formato DIAN (TXT)
                try:
                    archivo_dian = processor.generar_formato_dian(
                        retenciones, 
                        OUTPUT_DIR
                    )
                    archivos_generados['dian'] = str(archivo_dian)
                except Exception as e:
                    archivos_generados['error_dian'] = str(e)
                
                # Generar Excel
                try:
                    excel_gen = ExcelGenerator()
                    periodo = retenciones[0].get('periodo') if retenciones else None
                    excel_path = excel_gen.generar_reporte_retenciones(
                        retenciones, 
                        periodo=periodo
                    )
                    archivos_generados['excel'] = str(excel_path)
                except Exception as e:
                    archivos_generados['error_excel'] = str(e)
                
                # Generar XML
                try:
                    xml_gen = XMLGenerator()
                    periodo = retenciones[0].get('periodo') if retenciones else None
                    xml_path = xml_gen.generar_xml_retenciones(
                        retenciones,
                        periodo=periodo
                    )
                    archivos_generados['xml'] = str(xml_path)
                except Exception as e:
                    archivos_generados['error_xml'] = str(e)
            
            # Limpiar archivo temporal
            background_tasks.add_task(lambda: file_path.unlink(missing_ok=True))
            
            return {
                "status": "success",
                "tipo_archivo": "csv",
                "resumen": resumen,
                "archivos_generados": archivos_generados,
                "muestra_retenciones": retenciones[:10] if retenciones else []
            }
        
        else:
            # ================================================================
            # PROCESAR EXCEL (Formato específico de retenciones)
            # ================================================================
            service = RetencionService(db)
            resultado = service.procesar_desde_excel(file_path)
            
            # Generar archivos si hay retenciones procesadas
            archivos_generados = {}
            if resultado['procesados'] > 0:
                retenciones = resultado['detalles']
                
                # Generar formato DIAN (TXT)
                try:
                    archivo_dian = service.generar_formato_dian(
                        retenciones, 
                        OUTPUT_DIR
                    )
                    archivos_generados['dian'] = str(archivo_dian)
                except Exception as e:
                    archivos_generados['error_dian'] = str(e)
                
                # Generar Excel
                try:
                    excel_gen = ExcelGenerator()
                    archivos_excel = excel_gen.generar_reporte_por_tipo(retenciones, periodo)
                    archivos_generados['excel'] = {tipo: str(path) for tipo, path in archivos_excel.items()}
                except Exception as e:
                    archivos_generados['error_excel'] = str(e)

# 3. Generar XML (separados por tipo)
                try:
                    xml_gen = XMLGenerator()
                    archivos_xml = xml_gen.generar_xml_por_tipo(retenciones, periodo)
                    archivos_generados['xml'] = {tipo: str(path) for tipo, path in archivos_xml.items()}
                except Exception as e:
                    archivos_generados['error_xml'] = str(e)
            
            # Limpiar archivo temporal
            background_tasks.add_task(lambda: file_path.unlink(missing_ok=True))
            
            return {
                "status": "success",
                "tipo_archivo": "excel",
                "resultado": resultado,
                "archivos_generados": archivos_generados
            }
    
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        try:
            file_path.unlink(missing_ok=True)
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS DE CONSULTA
# ============================================================================

@router.get("/", response_model=RetencionListResponse)
async def listar_retenciones(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    periodo: Optional[str] = Query(None, description="Filtrar por período (YYYY-MM)"),
    nit_tercero: Optional[str] = Query(None, description="Filtrar por NIT del tercero"),
    db: Session = Depends(get_db)
):
    """
    Listar retenciones con paginación y filtros
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **periodo**: Filtrar por período (YYYY-MM)
    - **nit_tercero**: Filtrar por NIT del tercero
    """
    query = db.query(Retencion)
    
    if periodo:
        query = query.filter(Retencion.periodo == periodo)
    
    if nit_tercero:
        query = query.filter(Retencion.nit_tercero == nit_tercero)
    
    total = query.count()
    items = query.order_by(desc(Retencion.fecha)).offset(skip).limit(limit).all()
    
    return RetencionListResponse(
        total=total,
        items=[RetencionResponse.model_validate(item) for item in items],
        page=(skip // limit) + 1 if limit > 0 else 1,
        per_page=limit
    )


@router.get("/periodo/{periodo}", response_model=List[RetencionResponse])
async def obtener_retenciones_por_periodo(
    periodo: str,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las retenciones de un período específico
    
    - **periodo**: Período en formato YYYY-MM
    """
    service = RetencionService(db)
    retenciones = service.obtener_retenciones_por_periodo(periodo)
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron retenciones para el período {periodo}"
        )
    
    return [RetencionResponse.model_validate(r) for r in retenciones]


# ============================================================================
# ENDPOINTS DE RESUMEN Y ESTADÍSTICAS
# ============================================================================

@router.get("/resumen/conceptos", response_model=List[RetencionResumenPorConcepto])
async def resumen_por_concepto(
    periodo: Optional[str] = Query(None, description="Período específico (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Resumen de retenciones agrupadas por concepto DIAN
    
    - **periodo**: Período específico (YYYY-MM)
    """
    query = db.query(
        Retencion.concepto_dian,
        func.count(Retencion.id).label('cantidad'),
        func.sum(Retencion.base_gravable).label('total_base'),
        func.sum(Retencion.valor_retenido).label('total_retenido')
    ).group_by(Retencion.concepto_dian)
    
    if periodo:
        query = query.filter(Retencion.periodo == periodo)
    
    resultados = query.all()
    
    return [
        RetencionResumenPorConcepto(
            concepto_dian=r.concepto_dian,
            concepto_nombre=CONCEPTOS_RETENCION_DIAN.get(r.concepto_dian, f"Concepto {r.concepto_dian}"),
            cantidad=r.cantidad,
            total_base=float(r.total_base) if r.total_base else 0,
            total_retenido=float(r.total_retenido) if r.total_retenido else 0
        )
        for r in resultados
    ]


@router.get("/resumen/periodos", response_model=List[RetencionResumenPorPeriodo])
async def resumen_por_periodo(
    db: Session = Depends(get_db)
):
    """
    Resumen de retenciones agrupadas por período
    """
    query = db.query(
        Retencion.periodo,
        func.count(Retencion.id).label('cantidad'),
        func.sum(Retencion.valor_retenido).label('total_retenido')
    ).group_by(Retencion.periodo).order_by(Retencion.periodo)
    
    resultados = query.all()
    
    return [
        RetencionResumenPorPeriodo(
            periodo=r.periodo,
            total_retenido=float(r.total_retenido) if r.total_retenido else 0,
            cantidad=r.cantidad
        )
        for r in resultados
    ]


@router.get("/estadisticas")
async def obtener_estadisticas(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales de retenciones
    """
    total = db.query(Retencion).count()
    total_retenido = db.query(func.sum(Retencion.valor_retenido)).scalar() or 0
    
    ultimo_periodo = db.query(Retencion.periodo).order_by(desc(Retencion.periodo)).first()
    
    periodos = [r[0] for r in db.query(Retencion.periodo).distinct().order_by(Retencion.periodo).all()]
    
    return {
        "total_retenciones": total,
        "total_retenido": float(total_retenido),
        "ultimo_periodo": ultimo_periodo[0] if ultimo_periodo else None,
        "periodos_disponibles": periodos,
        "promedio_por_periodo": float(total_retenido / len(periodos)) if periodos else 0
    }


# ============================================================================
# ENDPOINTS DE GENERACIÓN DE ARCHIVOS
# ============================================================================

@router.post("/generar-formato/{periodo}")
async def generar_formato_dian(
    periodo: str,
    db: Session = Depends(get_db)
):
    """
    Generar archivo en formato DIAN (1003) para un período específico
    
    - **periodo**: Período en formato YYYY-MM
    """
    service = RetencionService(db)
    retenciones = service.obtener_retenciones_por_periodo(periodo)
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail=f"No hay retenciones para el período {periodo}"
        )
    
    output_path = service.generar_formato_dian(retenciones, OUTPUT_DIR)
    
    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type="text/plain"
    )


@router.post("/generar-reporte/{periodo}")
async def generar_reporte_excel(
    periodo: str,
    db: Session = Depends(get_db)
):
    """
    Generar reporte en Excel para un período específico
    
    - **periodo**: Período en formato YYYY-MM
    """
    service = RetencionService(db)
    retenciones = service.obtener_retenciones_por_periodo(periodo)
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail=f"No hay retenciones para el período {periodo}"
        )
    
    excel_gen = ExcelGenerator()
    excel_path = excel_gen.generar_reporte_retenciones(retenciones, periodo=periodo)
    
    return FileResponse(
        path=excel_path,
        filename=excel_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/generar-xml/{periodo}")
async def generar_xml_retenciones(
    periodo: str,
    db: Session = Depends(get_db)
):
    """
    Generar XML de retenciones para un período específico
    
    - **periodo**: Período en formato YYYY-MM
    """
    service = RetencionService(db)
    retenciones = service.obtener_retenciones_por_periodo(periodo)
    
    if not retenciones:
        raise HTTPException(
            status_code=404,
            detail=f"No hay retenciones para el período {periodo}"
        )
    
    xml_gen = XMLGenerator()
    xml_path = xml_gen.generar_xml_retenciones(retenciones, periodo=periodo)
    
    return FileResponse(
        path=xml_path,
        filename=xml_path.name,
        media_type="application/xml"
    )


# ============================================================================
# ENDPOINTS DE DESCARGA DE ARCHIVOS
# ============================================================================

@router.get("/descargar/excel/{filename}")
async def descargar_excel(filename: str):
    """
    Descargar un archivo Excel generado
    
    - **filename**: Nombre del archivo (ej: 20260821_ReteFuente_2025-01.xlsx)
    """
    file_path = Path("outputs/excel") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/descargar/xml/{filename}")
async def descargar_xml(filename: str):
    """
    Descargar un archivo XML generado
    
    - **filename**: Nombre del archivo (ej: 20260821_ReteFuente_2025-01.xml)
    """
    file_path = Path("outputs/xml") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/xml"
    )


@router.get("/descargar/dian/{filename}")
async def descargar_dian(filename: str):
    """
    Descargar un archivo DIAN (TXT) generado
    
    - **filename**: Nombre del archivo (ej: formato_1003_20250821.txt)
    """
    file_path = Path("outputs") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain"
    )