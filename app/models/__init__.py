# ============================================================================
# MODELS/__INIT__.PY
# OBJETIVO: Archivo de inicialización del paquete models.
#           Importa todos los modelos para que estén disponibles cuando se
#           importe el paquete. Alembic lo usará para detectar los modelos.
# ============================================================================

from app.models.mapping_rule import MappingRule

__all__ = ["MappingRule"]