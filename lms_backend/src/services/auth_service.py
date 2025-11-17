from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.auth.security import hash_password, verify_password


# PUBLIC_INTERFACE
async def signup(db: AsyncIOMotorDatabase, email: str, password: str, name: str, role: str = "student") -> str:
    """Create a new user and return its id. Note: In Supabase mode this endpoint is deprecated."""
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
    """Validate credentials and return user dict if valid. Deprecated in Supabase mode."""
    user = await db["users"].find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user.get("password_hash", "")):
        return None
    user["id"] = str(user["_id"])
    user.pop("_id", None)
    user.pop("password_hash", None)
    return user
