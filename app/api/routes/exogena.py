# ============================================================================
# API/ROUTES/EXOGENA.PY
# OBJETIVO: Endpoints para procesamiento de información exógena.
#           Incluye carga de CSV, procesamiento y generación de reportes.
# ============================================================================

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid

from app.core.database import get_db
from app.services.csv_processor import CSVProcessor
from app.schemas.exogena import CSVUploadResponse, ProcessingResult

router = APIRouter(prefix="/exogena", tags=["Procesamiento Exógena"])

@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo CSV para procesamiento de información exógena.
    
    El archivo debe tener las siguientes columnas:
    - nit_tercero: NIT del tercero
    - nombre_tercero: Nombre del tercero
    - valor: Valor de la transacción
    - codigo_puc: Código de cuenta contable PUC
    
    Returns:
        CSVUploadResponse con los resultados del procesamiento
    """
    # 1. Validar que el archivo es CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser de tipo CSV"
        )
    
    # 2. Guardar el archivo temporalmente
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        # Guardar archivo
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Procesar el archivo
        processor = CSVProcessor(db)
        processed_data, result = processor.process_file(str(file_path))
        
        # 4. Guardar resultados en archivo JSON para consulta futura
        import json
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{file_id}_result.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump({
                "file_id": file_id,
                "result": result.model_dump(),
                "data": processed_data
            }, f, ensure_ascii=False, indent=2)
        
        # 5. Retornar respuesta
        return CSVUploadResponse(
            message="Archivo procesado exitosamente",
            file_id=file_id,
            result=result
        )
        
    except Exception as e:
        # Limpiar archivo en caso de error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
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