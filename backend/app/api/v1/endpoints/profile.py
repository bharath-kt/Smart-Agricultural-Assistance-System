"""Farmer Profile API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import ProfileUpdate, ProfileResponse
from app.services.profile_service import profile_service
from app.core.security import get_current_user

router = APIRouter(prefix="/profile", tags=["Farmer Profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve logged-in farmer's profile."""
    profile = await profile_service.get_or_create_profile(db, current_user)
    return profile_service.format_profile_response(current_user, profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update logged-in farmer's profile."""
    return await profile_service.update_profile(db, current_user, data)
