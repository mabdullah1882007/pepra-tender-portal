from pydantic_settings import BaseSettings
import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    APP_NAME: str = "Tender Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = f"sqlite:///{os.path.join(BACKEND_DIR, 'tender_portal.db')}"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "tender-portal-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = os.path.join(BACKEND_DIR, "uploads")

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
