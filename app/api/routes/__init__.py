# ============================================================================
# API/ROUTES/__INIT__.PY
# OBJETIVO: Exportar los routers para facilitar la importación.
# ============================================================================

from app.api.routes.mapping import router as mapping_router
from app.api.routes.exogena import router as exogena_router

__all__ = ["mapping_router", "exogena_router"]