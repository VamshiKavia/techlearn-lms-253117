from fastapi import APIRouter, Depends
from src.schemas.user import UserPublic
from src.auth.dependencies import get_current_user

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserPublic, summary="Get current user (Supabase)")
async def me(user=Depends(get_current_user)):
    """Return current authenticated user's public info from Supabase JWT."""
    # Name may not be present; use empty string default
    return UserPublic(id=user["id"], email=user["email"], name=user.get("name", ""), role=user.get("role", "student"))
