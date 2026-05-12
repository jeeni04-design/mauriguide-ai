from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "MauriGuide AI"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # AI
    GROQ_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""        # kept in case you add credits later

    # Django
    DJANGO_SECRET_KEY: str = ""
    DJANGO_API_URL: str = "http://127.0.0.1:8000"

    # Database
    DATABASE_URL: str = "sqlite:///./mauriguide_chat.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False

    # Chat
    MAX_CHAT_HISTORY: int = 50
    CHAT_TIMEOUT: int = 3600

    # Image
    MAX_IMAGE_SIZE: int = 5242880

    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings():
    settings = Settings()
    print(f"🔧 Loading .env from: {ENV_FILE}")
    print(f"🤖 Groq API Key configured: {'Yes' if settings.GROQ_API_KEY else 'No - check your .env!'}")
    return settings

settings = get_settings()