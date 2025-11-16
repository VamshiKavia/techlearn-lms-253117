from pydantic import BaseModel, Field, EmailStr


class UserPublic(BaseModel):
    id: str = Field(..., description="User ID")
    email: EmailStr
    name: str
    role: str
