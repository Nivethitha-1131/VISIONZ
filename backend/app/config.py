"""
VISIONZ Configuration Manager
Loads and manages environment variables
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    
    # AI Services
    LLAMA_BASE_URL: str = os.getenv("LLAMA_BASE_URL", "http://localhost:11434")
    LLAMA_MODEL: str = os.getenv("LLAMA_MODEL", "llama2")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", 300))
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # YOLOv6
    YOLO_MODEL: str = os.getenv("YOLO_MODEL", "yolov6s")
    YOLO_CONFIDENCE_THRESHOLD: float = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", 0.45))
    YOLO_DEVICE: str = os.getenv("YOLO_DEVICE", "cpu")
    
    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 500))
    ALLOWED_VIDEO_FORMATS: str = os.getenv("ALLOWED_VIDEO_FORMATS", ".mp4,.avi,.mov,.mkv")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
    
    # Add properties to provide lists when needed
    @property
    def cors_origins_list(self) -> list:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_formats_list(self) -> list:
        return [fmt.strip() for fmt in self.ALLOWED_VIDEO_FORMATS.split(",")]


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./logs", exist_ok=True)

print(f"[Config] Environment: {settings.ENVIRONMENT}")
print(f"[Config] Database: {settings.DATABASE_URL}")
print(f"[Config] CORS Origins: {settings.CORS_ORIGINS}")
print(f"[Config] Llama URL: {settings.LLAMA_BASE_URL}")
print(f"[Config] Rate Limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
