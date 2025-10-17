
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., description="Clave para firmar JWT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    MEDIA_ROOT: str = "./media"
    DATABASE_URL: str = "sqlite:///./audios.db"
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_TIMEOUT_SECONDS: int = 10
    PUBLIC_BASE_URL: Optional[str] = None
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
