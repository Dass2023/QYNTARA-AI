import os
import logging

# Try Pydantic Settings (V1 or V2 via pydantic-settings)
# If not available, fall back to simple class to avoid dependency hell.
try:
    from pydantic import BaseSettings
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    try:
        from pydantic_settings import BaseSettings
        PYDANTIC_SETTINGS_AVAILABLE = True
    except ImportError:
        PYDANTIC_SETTINGS_AVAILABLE = False

class Settings:
    # Core
    APP_NAME: str = "QYNTARA AI"
    # Security
    API_KEY: str = os.getenv("QYNTARA_API_KEY", "QYNTARA-X-777")
    SECRET_KEY: str = os.getenv("QYNTARA_SECRET_KEY", "b33f_qyntara_v6_deep_intel_antigravity")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 Hours
    
    # Paths
    UPLOAD_DIR: str = os.path.join("backend", "data", "uploads")
    VECTOR_DB_PATH: str = os.path.join("backend", "data", "vector_store")
    
    def __init__(self):
        # Ensure critical paths exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)

# Singleton
settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qyntara.config")
