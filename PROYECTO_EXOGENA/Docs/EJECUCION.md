# 1. Actualizar pyproject.toml (copiar el contenido de arriba)

# 2. Limpiar y reinstalar

poetry update

# 3. Verificar
poetry run python -c "import pandas; print('✅ OK')"

# 4. Iniciar
poetry run python run.py
