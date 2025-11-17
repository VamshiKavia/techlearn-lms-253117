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
    """Create Motor client and initialize database/collections."""
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
    """Return active database object."""
    assert _db is not None, "Database not initialized"
    return _db
