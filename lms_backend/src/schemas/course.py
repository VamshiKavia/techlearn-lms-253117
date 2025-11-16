from typing import List, Optional
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, description="Course title")
    description: Optional[str] = Field(default=None, description="Course description")
    categories: List[str] = Field(default_factory=list, description="Categories/tags")


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Course title")
    description: Optional[str] = Field(default=None, description="Course description")
    categories: Optional[List[str]] = Field(default=None, description="Categories/tags")


class CoursePublic(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    categories: List[str] = []
    instructor_id: str
