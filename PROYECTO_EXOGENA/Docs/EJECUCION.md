# 1. Actualizar pyproject.toml (copiar el contenido de arriba)

# 2. Limpiar y reinstalar

poetry update

# 3. Verificar
poetry run python -c "import pandas; print('✅ OK')"

# 4. Iniciar
poetry run python run.py

uvicorn app.main:app --reload
python scripts/unificar_reglas.py
python scripts/generar_constants.py
python scripts/cargar_reglas.py