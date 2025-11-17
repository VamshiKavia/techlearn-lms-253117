from functools import lru_cache
import os
from typing import List, Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    APP_NAME: str = Field(default="TechLearn LMS Backend")
    APP_ENV: str = Field(default="development")
    APP_DEBUG: bool = Field(default=False)
    PORT: int = Field(default=3001)

    # Database (optional for now)
    MONGODB_URI: str = Field(default="")
    MONGODB_DB_NAME: str = Field(default="techlearn_lms")
    DB_AVAILABLE: bool = Field(default=False)

    # Supabase Auth (required)
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    SUPABASE_JWKS_URL: Optional[str] = Field(default=None, description="Optional override for JWKS URL")

    # Legacy JWT fields retained only where referenced, but not required anymore
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
    supabase_url = os.getenv("SUPABASE_URL", "")
    jwks_url = os.getenv("SUPABASE_JWKS_URL") or (f"{supabase_url}/auth/v1/jwks" if supabase_url else None)
    mongodb_uri = os.getenv("MONGODB_URI", "")
    db_available = bool(mongodb_uri)

    return Settings(
        APP_NAME=os.getenv("APP_NAME", "TechLearn LMS Backend"),
        APP_ENV=os.getenv("APP_ENV", "development"),
        APP_DEBUG=os.getenv("APP_DEBUG", "false").lower() == "true",
        PORT=int(os.getenv("PORT", "3001")),

        MONGODB_URI=mongodb_uri,
        MONGODB_DB_NAME=os.getenv("MONGODB_DB_NAME", "techlearn_lms"),
        DB_AVAILABLE=db_available,

        SUPABASE_URL=supabase_url,
        SUPABASE_KEY=os.getenv("SUPABASE_KEY", ""),
        SUPABASE_JWKS_URL=jwks_url,

        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        REFRESH_TOKEN_EXPIRE_MINUTES=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))),
        CORS_ALLOWED_ORIGINS=origin_list,
        RATE_LIMIT_ENABLE=os.getenv("RATE_LIMIT_ENABLE", "false").lower() == "true",
    )


settings = get_settings()


def validate_settings_or_exit() -> None:
    """Validate required settings on startup.
    - Require Supabase URL and Key
    - MongoDB is optional: if missing, set DB_AVAILABLE to False and continue
    """
    missing = []
    if not settings.SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not settings.SUPABASE_KEY:
        missing.append("SUPABASE_KEY")

    # MongoDB is optional; ensure DB_AVAILABLE flag reflects state
    if not settings.MONGODB_URI:
        # mutate cached settings flag to False if not provided
        settings.DB_AVAILABLE = False

    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
