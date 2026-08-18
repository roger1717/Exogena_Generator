# ============================================================================
# API/ROUTES/EXOGENA.PY
# OBJETIVO: Endpoints para procesamiento de información exógena.
#           Ahora con detección automática de columnas y sin column_mapping.
# ============================================================================

import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.csv_processor import CSVProcessor
from app.schemas.exogena import CSVUploadResponse

router = APIRouter(prefix="/exogena", tags=["Procesamiento Exógena"])


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo CSV para procesamiento de información exógena.
    
    **¡No necesita column_mapping!** El sistema detecta automáticamente las columnas.
    
    El archivo debe contener al menos:
    - Una columna con NIT/Identificación del tercero
    - Una columna con el nombre del tercero
    - Una columna numérica con el valor
    - Una columna con el código PUC
    
    Returns:
        CSVUploadResponse con los resultados del procesamiento
    """
    # 1. Validar que el archivo es CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    # 2. Crear carpetas necesarias
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # 3. Guardar el archivo temporalmente
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        # Guardar archivo
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 4. Procesar el archivo (sin column_mapping, detección automática)
        processor = CSVProcessor(db)
        processed_data, result = processor.process_file(str(file_path))
        
        # 5. Guardar resultados en archivo JSON para consulta futura
        output_file = output_dir / f"{file_id}_result.json"
        with output_file.open("w", encoding="utf-8") as f:
            # Convertir datetime a string para JSON
            result_dict = result.model_dump()
            # Asegurar que timestamp sea string
            if 'timestamp' in result_dict and isinstance(result_dict['timestamp'], datetime):
                result_dict['timestamp'] = result_dict['timestamp'].isoformat()
            
            json.dump({
                "file_id": file_id,
                "filename": file.filename,
                "result": result_dict,
                "data": processed_data,
                "mapping_used": "auto_detected"
            }, f, ensure_ascii=False, indent=2)
        
        # 6. Retornar respuesta
        return CSVUploadResponse(
            message="Archivo procesado exitosamente",
            file_id=file_id,
            result=result
        )
        
    except ValueError as e:
        # Error de validación (columnas faltantes, etc.)
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el formato del archivo: {str(e)}"
        )
        
    except Exception as e:
        # Error general
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
        )


@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analiza un archivo CSV y sugiere qué columnas usar para cada campo.
    
    Útil para verificar qué detectó el sistema automáticamente.
    """
    # Validar que el archivo es CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    # Guardar archivo temporalmente
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analizar el archivo
        processor = CSVProcessor(db)
        suggestions = processor.get_column_suggestions(str(file_path))
        
        # Limpiar archivo temporal
        file_path.unlink()
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "suggestions": suggestions
        }
        
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar el archivo: {str(e)}"
        )


@router.get("/results/{file_id}")
async def get_processing_results(file_id: str):
    """
    Obtiene los resultados de procesamiento de un archivo específico.
    """
    output_dir = Path("outputs")
    output_file = output_dir / f"{file_id}_result.json"
    
    if not output_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultados no encontrados"
        )
    
    with output_file.open("r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/sample")
async def generate_sample_csv(db: Session = Depends(get_db)):
    """
    Genera un archivo CSV de ejemplo para pruebas.
    """
    processor = CSVProcessor(db)
    file_path = processor.generate_sample_csv()
    
    return {
        "message": "Archivo de ejemplo generado exitosamente",
        "file_path": file_path
    }


@router.get("/download-sample")
async def download_sample_csv():
    """
    Descarga el archivo CSV .
    """
    file_path = Path("uploads/sample_data.csv")
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de ejemplo no encontrado. Ejecuta primero GET /exogena/sample"
        )
    
    return FileResponse(
        path=file_path,
        filename="sample_data.csv",
        media_type="text/csv"
    )

@router.get("/download-excel/{file_id}")
async def download_excel(file_id: str, db: Session = Depends(get_db)):
    """
    Descarga un archivo Excel con el detalle y resumen de los datos procesados.
    """
    # Buscar el resultado guardado
    output_dir = Path("outputs")
    result_file = output_dir / f"{file_id}_result.json"
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Resultados no encontrados")
    
    with result_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    processed_data = data.get("data", [])
    if not processed_data:
        raise HTTPException(status_code=404, detail="No hay datos para generar el Excel")
    
    # Generar Excel
    processor = CSVProcessor(db)
    excel_path = processor.generate_excel(processed_data, file_id)
    
    return FileResponse(
        path=excel_path,
        filename=f"exogena_{file_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/download-xml/{file_id}")
async def download_xml(file_id: str, format_code: str = "1001", db: Session = Depends(get_db)):
    """
    Descarga un archivo XML para la DIAN en el formato especificado.
    Por defecto genera el formato 1001.
    """
    # Buscar el resultado guardado
    output_dir = Path("outputs")
    result_file = output_dir / f"{file_id}_result.json"
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Resultados no encontrados")
    
    with result_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    processed_data = data.get("data", [])
    if not processed_data:
        raise HTTPException(status_code=404, detail="No hay datos para generar el XML")
    
    # Generar XML
    processor = CSVProcessor(db)
    xml_path = processor.generate_xml(processed_data, file_id, format_code)
    
    return FileResponse(
        path=xml_path,
        filename=f"exogena_{format_code}_{file_id}.xml",
        media_type="application/xml"
    )