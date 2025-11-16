from functools import lru_cache
import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    APP_NAME: str = Field(default="TechLearn LMS Backend")
    APP_ENV: str = Field(default="development")
    APP_DEBUG: bool = Field(default=False)
    PORT: int = Field(default=3001)

    MONGODB_URI: str = Field(default="")
    MONGODB_DB_NAME: str = Field(default="techlearn_lms")

    JWT_SECRET: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)

    CORS_ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    RATE_LIMIT_ENABLE: bool = Field(default=False)

    class Config:
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    # Parse allowed origins from comma separated list
    origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    origin_list = [o.strip() for o in origins.split(",")] if origins else ["*"]
    return Settings(
        APP_NAME=os.getenv("APP_NAME", "TechLearn LMS Backend"),
        APP_ENV=os.getenv("APP_ENV", "development"),
        APP_DEBUG=os.getenv("APP_DEBUG", "false").lower() == "true",
        PORT=int(os.getenv("PORT", "3001")),
        MONGODB_URI=os.getenv("MONGODB_URI", ""),
        MONGODB_DB_NAME=os.getenv("MONGODB_DB_NAME", "techlearn_lms"),
        JWT_SECRET=os.getenv("JWT_SECRET", ""),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        REFRESH_TOKEN_EXPIRE_MINUTES=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))),
        CORS_ALLOWED_ORIGINS=origin_list,
        RATE_LIMIT_ENABLE=os.getenv("RATE_LIMIT_ENABLE", "false").lower() == "true",
    )


settings = get_settings()


def validate_settings_or_exit() -> None:
    """Validate required settings on startup and fail fast if missing."""
    missing = []
    if not settings.MONGODB_URI:
        missing.append("MONGODB_URI")
    if not settings.JWT_SECRET:
        missing.append("JWT_SECRET")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
