"""Application configuration settings."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")
    
    # App
    APP_NAME: str = "Smart Agriculture API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./smart_agri.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenWeatherMap
    OPENWEATHER_API_KEY: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security / JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-smart-agri-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

settings = Settings()
