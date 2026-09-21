# ============================================================================
# MIGRATIONS/ENV.PY
# OBJETIVO: Archivo de configuración de Alembic para ejecutar migraciones.
#           Configura el entorno de migración para usar nuestra aplicación.
#           Detecta automáticamente los modelos y genera las migraciones.
# ============================================================================

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import Base

# Importar todos los modelos para registrar las tablas en Base.metadata
from app.models import MappingRule, renta, retencion

# Configurar logging
config = context.config

# Sobrescribir la URL con la de nuestras settings (convertida a string por si se usa Pydantic)
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detecta modificaciones en los tipos de columna
        render_as_batch=True,  # Permite alteración de tablas en SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detecta modificaciones en los tipos de columna
            render_as_batch=True,  # Permite alteración de tablas en SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()