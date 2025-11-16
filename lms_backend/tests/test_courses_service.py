import pytest
from types import SimpleNamespace

from src.services.courses_service import create_course, list_courses, get_course, update_course, delete_course


class FakeCollection:
    def __init__(self):
        self.storage = {}
        self.counter = 0

    async def insert_one(self, doc):
        self.counter += 1
        _id = f"id{self.counter}"
        doc["_id"] = _id
        self.storage[_id] = doc
        return SimpleNamespace(inserted_id=_id)

    def find(self, query):
        class Cursor:
            def __init__(self, docs):
                self.docs = list(docs.values())

            def skip(self, n): return self

            def limit(self, n): return self

            async def __aiter__(self):
                for d in self.docs:
                    yield dict(d)

        return Cursor(self.storage)

    async def find_one(self, query):
        _id = query.get("_id")
        return self.storage.get(_id)

    async def update_one(self, query, update):
        _id = query.get("_id")
        if _id in self.storage:
            self.storage[_id].update(update["$set"])
            return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)

    async def delete_one(self, query):
        _id = query.get("_id")
        if _id in self.storage:
            del self.storage[_id]
            return SimpleNamespace(deleted_count=1)
        return SimpleNamespace(deleted_count=0)


class FakeDB(dict):
    def __init__(self):
        super().__init__({"courses": FakeCollection()})


@pytest.mark.asyncio
async def test_courses_crud_flow():
    # Arrange
    db = FakeDB()
    # Act
    cid = await create_course(db, "instructor1", {"title": "T1", "description": "D", "categories": ["cat"]})
    # Assert
    items = await list_courses(db)
    assert len(items) == 1
    got = await get_course(db, cid)
    assert got["title"] == "T1"
    updated = await update_course(db, cid, {"title": "T2"})
    assert updated is True
    deleted = await delete_course(db, cid)
    assert deleted is True
