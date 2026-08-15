# ============================================================================
# API/ROUTES/EXOGENA.PY
# OBJETIVO: Endpoints para procesamiento de información exógena.
#           Incluye carga de CSV, análisis de columnas y procesamiento.
# ============================================================================

import json
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.csv_processor import CSVProcessor
from app.schemas.exogena import CSVUploadResponse, ProcessingResult

router = APIRouter(prefix="/exogena", tags=["Procesamiento Exógena"])


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    column_mapping: Optional[str] = None,  # JSON con mapeo manual (opcional)
    db: Session = Depends(get_db)
):
    """
    Sube un archivo CSV para procesamiento de información exógena.
    
    Características:
    - Detecta automáticamente las columnas del CSV
    - Permite mapeo manual si se proporciona
    
    Args:
        file: Archivo CSV a procesar
        column_mapping: JSON con mapeo manual de columnas (opcional)
        db: Sesión de base de datos
    
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
        
        # 4. Parsear el mapeo manual si existe
        mapping = json.loads(column_mapping) if column_mapping else None
        
        # 5. Procesar el archivo
        processor = CSVProcessor(db, mapping)
        processed_data, result = processor.process_file(str(file_path))
        
        # 6. Guardar resultados en archivo JSON para consulta futura
        output_file = output_dir / f"{file_id}_result.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump({
                "file_id": file_id,
                "filename": file.filename,
                "result": result.model_dump(),
                "data": processed_data,
                "mapping_used": mapping or "auto_detected"
            }, f, ensure_ascii=False, indent=2)
        
        # 7. Retornar respuesta
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
    
    Útil para que el usuario confirme el mapeo antes de procesar.
    
    Args:
        file: Archivo CSV a analizar
        db: Sesión de base de datos
    
    Returns:
        Sugerencias de mapeo de columnas
    """
    # 1. Validar que el archivo es CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    # 2. Guardar archivo temporalmente
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Analizar el archivo
        processor = CSVProcessor(db)
        suggestions = processor.get_column_suggestions(str(file_path))
        
        # 4. Limpiar archivo temporal
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
async def get_processing_results(
    file_id: str
):
    """
    Obtiene los resultados de procesamiento de un archivo específico.
    
    Args:
        file_id: ID del archivo generado en la carga
        
    Returns:
        Resultados del procesamiento
    """
    import json
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
async def generate_sample_csv(
    db: Session = Depends(get_db)
):
    """
    Genera un archivo CSV de ejemplo para pruebas.
    
    Returns:
        Información del archivo generado
    """
    processor = CSVProcessor(db)
    file_path = processor.generate_sample_csv()
    
    return {
        "message": "Archivo de ejemplo generado exitosamente",
        "file_path": file_path,
        "download_url": f"/download-sample"
    }

@router.get("/download-sample")
async def download_sample_csv():
    """
    Descarga el archivo CSV de ejemplo.
    """
    from fastapi.responses import FileResponse
    
    file_path = Path("uploads/sample_data.csv")
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de ejemplo no encontrado"
        )
    
    return FileResponse(
        path=file_path,
        filename="sample_data.csv",
        media_type="text/csv"
    )

@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analiza un archivo CSV y sugiere qué columnas usar para cada campo.
    Útil para que el usuario confirme el mapeo antes de procesar.
    """
    # Guardar archivo temporal
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analizar
    processor = CSVProcessor(db)
    suggestions = processor.get_column_suggestions(str(file_path))
    
    # Limpiar archivo temporal
    file_path.unlink()
    
    return {
        "file_id": file_id,
        "suggestions": suggestions
    }