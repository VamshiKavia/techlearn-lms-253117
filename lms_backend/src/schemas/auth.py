from pydantic import BaseModel, Field, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Plain password")
    name: str = Field(..., min_length=1, description="Full name")
    role: str = Field("student", description="Role: admin, instructor, or student")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Plain password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")
