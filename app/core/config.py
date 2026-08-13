import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    """Configuración de la aplicación usando variables de entorno."""
    
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "Exogena MVP")
        self.APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./exogena.db")
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
    
    def validate(self):
        """Validar configuración."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL no está configurada")
        return True

# Crear instancia global
settings = Settings()
settings.validate()