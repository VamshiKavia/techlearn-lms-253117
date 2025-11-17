from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.db.mongodb import get_db
from src.schemas.auth import SignupRequest, TokenResponse, RefreshRequest
from src.schemas.user import UserPublic
from src.services.auth_service import signup as svc_signup, authenticate, issue_tokens, refresh_tokens
from src.auth.dependencies import get_current_user

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("/signup", response_model=UserPublic, summary="User signup")
async def signup(payload: SignupRequest):
    """Register a new user; returns public user info."""
    db = get_db()
    try:
        user_id = await svc_signup(db, payload.email, payload.password, payload.name, payload.role)
        return UserPublic(id=user_id, email=payload.email, name=payload.name, role=payload.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# PUBLIC_INTERFACE
@router.post("/login", response_model=TokenResponse, summary="User login with credentials")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login using OAuth2 form (username=email)."""
    db = get_db()
    user = await authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return issue_tokens(user["id"])


# PUBLIC_INTERFACE
@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(payload: RefreshRequest):
    """Refresh tokens using a valid refresh token."""
    try:
        return refresh_tokens(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserPublic, summary="Get current user")
async def me(user=Depends(get_current_user)):
    """Return current authenticated user's public info."""
    return UserPublic(id=user["id"], email=user["email"], name=user.get("name", ""), role=user.get("role", "student"))
