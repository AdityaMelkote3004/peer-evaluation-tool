"""Core configuration management using Pydantic settings."""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Database
    DATABASE_URL: str
    ASYNC_DATABASE_URL: str
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
