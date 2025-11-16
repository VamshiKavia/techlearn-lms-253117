from fastapi import APIRouter

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/health", summary="Health Check")
async def health() -> dict:
    """Return service health status."""
    return {"status": "OK"}
