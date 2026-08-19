# ============================================================================
# CORE/DATABASE.PY
# OBJETIVO: Configurar la conexión a la base de datos PostgreSQL usando SQLAlchemy.
#           Crea el motor de conexión, la fábrica de sesiones y el base declarativa
#           para los modelos. Proporciona una función para obtener la sesión
#           de base de datos en los endpoints de FastAPI.
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# Crear el motor de conexión - Configuración especial para SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para definir modelos
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Función para obtener la sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()