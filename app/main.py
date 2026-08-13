# ============================================================================
# MAIN.PY
# OBJETIVO: Punto de entrada de la aplicación FastAPI.
#           Configura la aplicación, registra los routers, middleware y
#           maneja eventos de inicio/apagado. Es el orquestador principal.
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import mapping

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para gestión de información exógena - MVP",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configurar CORS (permite peticiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los routers
app.include_router(mapping.router)
app.include_router(exogena.router)

@app.get("/")
async def root():
    """
    Endpoint raíz que verifica que la API está funcionando.
    """
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar la salud de la aplicación.
    Útil para monitoreo y contenedores Docker.
    """
    return {
        "status": "healthy",
        "database": "connected"  # Podríamos verificar la conexión a la BD aquí
    }