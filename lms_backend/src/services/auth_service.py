from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


# PUBLIC_INTERFACE
async def signup(db: AsyncIOMotorDatabase, email: str, password: str, name: str, role: str = "student") -> str:
    """Create a new user and return its id."""
    existing = await db["users"].find_one({"email": email})
    if existing:
        raise ValueError("Email already registered")
    user = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "role": role if role in ("admin", "instructor", "student") else "student",
        "created_at": datetime.utcnow(),
    }
    res = await db["users"].insert_one(user)
    return str(res.inserted_id)


# PUBLIC_INTERFACE
async def authenticate(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[dict]:
    """Validate credentials and return user dict if valid."""
    user = await db["users"].find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user.get("password_hash", "")):
        return None
    user["id"] = str(user["_id"])
    user.pop("_id", None)
    user.pop("password_hash", None)
    return user


# PUBLIC_INTERFACE
def issue_tokens(user_id: str) -> dict:
    """Create access and refresh tokens for a user id."""
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


# PUBLIC_INTERFACE
def refresh_tokens(refresh_token: str) -> dict:
    """Issue new tokens from a valid refresh token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token")
    return issue_tokens(user_id)
