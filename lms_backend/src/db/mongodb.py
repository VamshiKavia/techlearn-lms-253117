from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core.config import settings
from src.utils.logging import logger

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

COLLECTIONS = [
    "users",
    "roles",
    "courses",
    "modules",
    "lessons",
    "enrollments",
    "progress",
    "reviews",
    "announcements",
    "assignments",
    "quizzes",
]


# PUBLIC_INTERFACE
async def connect_to_mongo() -> None:
    """Create Motor client and initialize database/collections.

    Behavior:
    - If DB not configured (settings.DB_AVAILABLE False), skip gracefully.
    - If connection fails, log warning and continue startup (non-blocking).
    """
    if not settings.DB_AVAILABLE:
        logger.warning({"msg": "MongoDB not configured. Skipping DB initialization."})
        return
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client.get_database(settings.MONGODB_DB_NAME)
        # Create collections if not existing by listing once
        existing = set(await db.list_collection_names())
        for name in COLLECTIONS:
            if name not in existing:
                await db.create_collection(name)
        # assign to module-level references without redeclaring globals (avoids F824)
        globals()["_client"] = client
        globals()["_db"] = db
        logger.info({"msg": "Connected to MongoDB", "db": settings.MONGODB_DB_NAME})
    except Exception as e:
        # Do not block app startup
        logger.warning({"msg": "MongoDB connection failed; continuing without DB", "error": str(e)})
        globals()["_client"] = None
        globals()["_db"] = None
        settings.DB_AVAILABLE = False


# PUBLIC_INTERFACE
async def close_mongo_connection() -> None:
    """Close Motor client connection."""
    client = globals().get("_client")
    if client:
        client.close()
        logger.info({"msg": "MongoDB connection closed"})
        globals()["_client"] = None
        globals()["_db"] = None


# PUBLIC_INTERFACE
def get_db() -> AsyncIOMotorDatabase:
    """Return active database object.

    Raises:
        AssertionError: if database has not been initialized (DB unavailable).
    """
    assert _db is not None, "Database not initialized"
    return _db
