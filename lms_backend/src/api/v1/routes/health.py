from fastapi import APIRouter
from src.core.config import settings

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/health", summary="Health Check")
async def health() -> dict:
    """Return service health status.

    Provides a lightweight readiness/liveness signal that does not depend on external services.
    """
    return {
        "status": "OK",
        "db_available": settings.DB_AVAILABLE,
        "auth": "supabase",
        "env": settings.APP_ENV,
    }
