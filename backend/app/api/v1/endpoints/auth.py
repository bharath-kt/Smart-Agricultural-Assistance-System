"""Authentication API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import auth_service
from app.services.profile_service import profile_service
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Farmer Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/signup/", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register/", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new farmer account with initial profile."""
    return await auth_service.signup(db, request)


@router.post("/login", response_model=TokenResponse)
@router.post("/login/", response_model=TokenResponse, include_in_schema=False)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Log in an existing farmer account using email or mobile number."""
    return await auth_service.login(db, request)


@router.get("/me", response_model=UserResponse)
@router.get("/me/", response_model=UserResponse, include_in_schema=False)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get logged in farmer profile and account details."""
    profile = await profile_service.get_or_create_profile(db, current_user)
    prof_resp = profile_service.format_profile_response(current_user, profile)
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        mobile_number=current_user.mobile_number,
        is_active=current_user.is_active,
        profile=prof_resp
    )

