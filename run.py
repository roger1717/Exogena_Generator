# ============================================================================
# RUN.PY
# OBJETIVO: Script para iniciar la aplicación FastAPI en modo desarrollo.
#           Ejecuta Uvicorn con recarga automática (hot reload) para que los
#           cambios en el código se reflejen sin reiniciar manualmente.
# ============================================================================

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Recarga automática si DEBUG=True
        log_level="info"
    )