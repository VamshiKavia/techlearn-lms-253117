from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.db.repository import insert_one, find_many, find_one, update_one, delete_one


# PUBLIC_INTERFACE
async def create_course(db: AsyncIOMotorDatabase, instructor_id: str, data: Dict[str, Any]) -> str:
    """Create a new course."""
    course = {
        "title": data["title"],
        "description": data.get("description"),
        "categories": data.get("categories", []),
        "instructor_id": instructor_id,
    }
    return await insert_one(db["courses"], course)


# PUBLIC_INTERFACE
async def list_courses(db: AsyncIOMotorDatabase, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """List public courses."""
    return await find_many(db["courses"], {}, limit=limit, skip=skip)


# PUBLIC_INTERFACE
async def get_course(db: AsyncIOMotorDatabase, course_id: str) -> Optional[Dict[str, Any]]:
    """Get course by id."""
    return await find_one(db["courses"], {"_id": course_id})


# PUBLIC_INTERFACE
async def update_course(db: AsyncIOMotorDatabase, course_id: str, updates: Dict[str, Any]) -> bool:
    """Update a course."""
    return await update_one(db["courses"], course_id, updates)


# PUBLIC_INTERFACE
async def delete_course(db: AsyncIOMotorDatabase, course_id: str) -> bool:
    """Delete a course."""
    return await delete_one(db["courses"], course_id)
