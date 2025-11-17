from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from src.auth.supabase_verifier import verify_supabase_jwt
from src.core.config import settings

security_scheme = HTTPBearer(auto_error=False)

ROLES = ("admin", "instructor", "student")


# PUBLIC_INTERFACE
async def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> Dict[str, Any]:
    """Return current authenticated user using Supabase JWT verification.

    Extracts Bearer token from Authorization header, verifies via Supabase JWKS, validates claims,
    and returns a normalized user dict: {id, email, role, raw_claims}.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    try:
        payload = await verify_supabase_jwt(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token (no sub)")

        email = payload.get("email") or payload.get("user_metadata", {}).get("email")
        # Roles can be set in app_metadata.role or custom claim; fallback to 'student'
        role = (
            payload.get("app_metadata", {}).get("role")
            or payload.get("role")
            or "student"
        )

        user: Dict[str, Any] = {
            "id": user_id,
            "email": email or "",
            "role": role if role in ROLES else "student",
            "claims": payload,
        }
        return user
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


# PUBLIC_INTERFACE
def require_roles(*allowed_roles: str):
    """Dependency factory to enforce RBAC based on Supabase JWT claims."""
    for r in allowed_roles:
        if r not in ROLES:
            raise ValueError(f"Unknown role: {r}")

    async def _dep(user=Depends(get_current_user)):
        role = user.get("role", "student")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _dep


# PUBLIC_INTERFACE
def require_db():
    """Dependency to enforce database availability. Raises 503 if DB is not configured."""
    from fastapi import HTTPException
    if not settings.DB_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured")
    return True
