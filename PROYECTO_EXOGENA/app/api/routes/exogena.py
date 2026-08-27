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

UPLOAD_DIR = Path("uploads")
OUTPUT_EXOGENA_DIR = Path("outputs/exogena")

# Garantizar existencia de directorios al iniciar
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_EXOGENA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processor = CSVProcessor(db)
        processed_data, result = processor.process_file(str(file_path))
        
        # 1. Generar Excel automáticamente en outputs/exogena
        excel_path = processor.generate_excel(processed_data, file_id)
        
        # 2. Guardar JSON resultado en outputs/exogena
        json_file_path = OUTPUT_EXOGENA_DIR / f"{file_id}_result.json"
        result_dict = result.model_dump()
        
        if 'timestamp' in result_dict and isinstance(result_dict['timestamp'], datetime):
            result_dict['timestamp'] = result_dict['timestamp'].isoformat()
            
        with json_file_path.open("w", encoding="utf-8") as f:
            json.dump({
                "file_id": file_id,
                "filename": file.filename,
                "excel_path": excel_path,
                "json_path": str(json_file_path),
                "result": result_dict,
                "data": processed_data,
                "mapping_used": "auto_detected"
            }, f, ensure_ascii=False, indent=2)
            
        return CSVUploadResponse(
            message="Archivo procesado y generado exitosamente",
            file_id=file_id,
            json_path=str(json_file_path),
            excel_path=excel_path,
            result=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el formato del archivo: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
        )
    finally:
        if file_path.exists():
            file_path.unlink()
        await file.close()


@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processor = CSVProcessor(db)
        suggestions = processor.get_column_suggestions(str(file_path))
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar el archivo: {str(e)}"
        )
    finally:
        # Garantiza que el archivo temporal siempre se elimine
        if file_path.exists():
            file_path.unlink()
        await file.close()

@router.get("/results/{file_id}")
async def get_processing_results(file_id: str):
    output_file = OUTPUT_EXOGENA_DIR / f"{file_id}_result.json"
    
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
async def download_excel(file_id: str):
    excel_path = OUTPUT_EXOGENA_DIR / f"{file_id}_resumen.xlsx"
    
    if not excel_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo Excel no encontrado. Verifica si el archivo fue procesado."
        )
    
    return FileResponse(
        path=excel_path,
        filename=f"exogena_{file_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/download-xml/{file_id}")
async def download_xml(file_id: str, format_code: str = "1001", db: Session = Depends(get_db)):
    result_file = OUTPUT_EXOGENA_DIR / f"{file_id}_result.json"
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Resultados no encontrados")
    
    with result_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    processed_data = data.get("data", [])
    if not processed_data:
        raise HTTPException(status_code=404, detail="No hay datos para generar el XML")
    
    processor = CSVProcessor(db)
    xml_path = processor.generate_xml(processed_data, file_id, format_code)
    
    return FileResponse(
        path=xml_path,
        filename=f"exogena_{format_code}_{file_id}.xml",
        media_type="application/xml"
    )