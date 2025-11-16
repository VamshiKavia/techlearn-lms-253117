from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


def _to_object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)


# PUBLIC_INTERFACE
async def insert_one(collection: AsyncIOMotorCollection, document: Dict[str, Any]) -> str:
    """Insert a document and return its id as string."""
    res = await collection.insert_one(document)
    return str(res.inserted_id)


# PUBLIC_INTERFACE
async def find_one(collection: AsyncIOMotorCollection, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a single document."""
    doc = await collection.find_one(query)
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


# PUBLIC_INTERFACE
async def find_many(collection: AsyncIOMotorCollection, query: Dict[str, Any], limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """Find many documents."""
    cursor = collection.find(query).skip(skip).limit(limit)
    items: List[Dict[str, Any]] = []
    async for doc in cursor:
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        items.append(doc)
    return items


# PUBLIC_INTERFACE
async def update_one(collection: AsyncIOMotorCollection, id_str: str, updates: Dict[str, Any]) -> bool:
    """Update a document by id; returns True if modified."""
    res = await collection.update_one({"_id": _to_object_id(id_str)}, {"$set": updates})
    return res.modified_count > 0


# PUBLIC_INTERFACE
async def delete_one(collection: AsyncIOMotorCollection, id_str: str) -> bool:
    """Delete a document by id; returns True if deleted."""
    res = await collection.delete_one({"_id": _to_object_id(id_str)})
    return res.deleted_count > 0
