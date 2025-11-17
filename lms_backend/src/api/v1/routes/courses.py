from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.db.mongodb import get_db
from src.schemas.course import CourseCreate, CourseUpdate, CoursePublic
from src.services.courses_service import create_course, list_courses, get_course, update_course, delete_course
from src.auth.dependencies import require_roles, require_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("", response_model=dict, summary="Create course")
async def create(payload: CourseCreate, user=Depends(require_roles("instructor", "admin")), _=Depends(require_db)):
    """Create a course; instructor or admin only."""
    db = get_db()
    course_id = await create_course(db, user["id"], payload.model_dump())
    return {"id": course_id}


# PUBLIC_INTERFACE
@router.get("", response_model=List[CoursePublic], summary="List courses")
async def list_all(_=Depends(require_db)):
    """List public courses."""
    db = get_db()
    items = await list_courses(db)
    return items  # already in public form


# PUBLIC_INTERFACE
@router.get("/{course_id}", response_model=CoursePublic, summary="Get course by id")
async def get_by_id(course_id: str, _=Depends(require_db)):
    """Get a course by id."""
    db = get_db()
    item = await get_course(db, course_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return item


# PUBLIC_INTERFACE
@router.put("/{course_id}", response_model=dict, summary="Update course")
async def update(course_id: str, payload: CourseUpdate, user=Depends(require_roles("instructor", "admin")), _=Depends(require_db)):
    """Update a course; instructor owner or admin."""
    db = get_db()
    existing = await get_course(db, course_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if user["role"] != "admin" and existing.get("instructor_id") != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not course owner")
    updated = await update_course(db, course_id, {k: v for k, v in payload.model_dump().items() if v is not None})
    return {"updated": updated}


# PUBLIC_INTERFACE
@router.delete("/{course_id}", response_model=dict, summary="Delete course")
async def delete(course_id: str, user=Depends(require_roles("admin")), _=Depends(require_db)):
    """Delete a course; admin only."""
    db = get_db()
    deleted = await delete_course(db, course_id)
    return {"deleted": deleted}
