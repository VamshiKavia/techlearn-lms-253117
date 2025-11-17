from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from src.auth.security import decode_token
from src.db.mongodb import get_db
from src.db.repository import find_one

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

ROLES = ("admin", "instructor", "student")


# PUBLIC_INTERFACE
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Return user from access token."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db = get_db()
        user = await find_one(db["users"], {"_id": user_id})  # this path expects string id; fallback below
        if not user:
            # fallback by converting string to ObjectId inside repository if needed
            user = await find_one(db["users"], {"id": user_id})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode failed")


# PUBLIC_INTERFACE
def require_roles(*allowed_roles: str):
    """Dependency factory to enforce RBAC."""
    for r in allowed_roles:
        if r not in ROLES:
            raise ValueError(f"Unknown role: {r}")

    async def _dep(user=Depends(get_current_user)):
        role = user.get("role", "student")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _dep
