from fastapi import APIRouter, Depends
from src.schemas.user import UserPublic
from src.auth.dependencies import get_current_user

router = APIRouter(tags=["auth"])


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserPublic, summary="Get current user (Supabase)", description="Return current authenticated user's public info from Supabase JWT.")
async def me(user=Depends(get_current_user)):
    """Return current authenticated user's public info from Supabase JWT."""
    # Name may not be present; use empty string default
    return UserPublic(id=user["id"], email=user["email"], name=user.get("name", ""), role=user.get("role", "student"))

# PUBLIC_INTERFACE
@router.get(
    "/debug",
    summary="Auth debug",
    description="Temporary endpoint to echo current auth status and normalized user. Use for integration verification.\n\nUsage:\n- Send Authorization: Bearer <supabase_jwt> header.\n- Confirms backend JWKS verification and CORS path.\n- If 401, check anon key validity and frontend token propagation.",
    responses={200: {"description": "Debug info with user and claims (if authenticated)."}, 401: {"description": "Missing or invalid token."}},
    name="auth_debug",
)
async def auth_debug(user=Depends(get_current_user)):
    """Return diagnostic information about the current authenticated user and claims.

    Returns:
        200 with { authenticated, user, claims } when token valid.
        401 if missing/invalid token (raised by dependency).
    """
    claims = user.get("claims", {})
    # Only include non-sensitive subset
    safe_claims = {
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "aud": claims.get("aud"),
        "iss": claims.get("iss"),
        "role": claims.get("app_metadata", {}).get("role") or claims.get("role"),
        "exp": claims.get("exp"),
        "iat": claims.get("iat"),
    }
    return {
        "authenticated": True,
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "role": user.get("role"),
        },
        "claims": safe_claims,
    }
