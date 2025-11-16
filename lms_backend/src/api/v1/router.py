from fastapi import APIRouter

from src.api.v1.routes import auth, courses, health

# Define OpenAPI tags metadata
tags_metadata = [
    {"name": "health", "description": "Service health and diagnostics."},
    {"name": "auth", "description": "Authentication and user account endpoints."},
    {"name": "courses", "description": "Course catalog and management."},
]

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
