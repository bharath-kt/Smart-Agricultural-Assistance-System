"""Farmer Profile service."""
import json
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, FarmerProfile
from app.models.history import UserActivityLog
from app.schemas.user import ProfileUpdate, ProfileResponse


class ProfileService:
    """Service for managing farmer profile."""

    async def get_or_create_profile(self, db: AsyncSession, user: User) -> FarmerProfile:
        result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
        profile = result.scalar_one_or_none()

        if not profile:
            profile = FarmerProfile(
                user_id=user.id,
                full_name=user.full_name or "Farmer",
                state=user.state or "Karnataka",
                district=user.district or "Mysuru",
                farmer_category="Small",
                land_ownership="Owned",
                land_size=1.5,
                crops_grown=json.dumps(["Tomato", "Paddy"]),
                annual_income=180000.0,
                irrigation_type="Well",
                farming_type="Conventional"
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return profile

    async def update_profile(self, db: AsyncSession, user: User, data: ProfileUpdate) -> ProfileResponse:
        profile = await self.get_or_create_profile(db, user)

        if data.full_name is not None:
            profile.full_name = data.full_name
            user.full_name = data.full_name
        if data.age is not None:
            profile.age = data.age
        if data.gender is not None:
            profile.gender = data.gender
        if data.state is not None:
            profile.state = data.state
            user.state = data.state
        if data.district is not None:
            profile.district = data.district
            user.district = data.district
        if data.farmer_category is not None:
            profile.farmer_category = data.farmer_category
        if data.land_ownership is not None:
            profile.land_ownership = data.land_ownership
        if data.land_size is not None:
            profile.land_size = data.land_size
        if data.crops_grown is not None:
            profile.crops_grown = json.dumps(data.crops_grown)
            user.preferred_crops = ",".join(data.crops_grown)
        if data.annual_income is not None:
            profile.annual_income = data.annual_income
        if data.irrigation_type is not None:
            profile.irrigation_type = data.irrigation_type
        if data.farming_type is not None:
            profile.farming_type = data.farming_type
        if data.additional_info is not None:
            profile.additional_info = data.additional_info

        # Log activity
        log = UserActivityLog(
            user_id=user.id,
            activity_type="profile_update",
            title="Profile Updated",
            description=f"Updated farmer profile for {user.full_name or 'Farmer'}."
        )
        db.add(log)
        await db.commit()
        await db.refresh(profile)

        return self.format_profile_response(user, profile)

    def format_profile_response(self, user: User, profile: FarmerProfile) -> ProfileResponse:
        crops_list = []
        if profile.crops_grown:
            try:
                crops_list = json.loads(profile.crops_grown)
            except Exception:
                crops_list = [c.strip() for c in profile.crops_grown.split(",") if c.strip()]

        return ProfileResponse(
            user_id=user.id,
            full_name=profile.full_name or user.full_name,
            email=user.email,
            mobile_number=user.mobile_number,
            age=profile.age,
            gender=profile.gender,
            state=profile.state or user.state,
            district=profile.district or user.district,
            farmer_category=profile.farmer_category,
            land_ownership=profile.land_ownership,
            land_size=profile.land_size,
            crops_grown=crops_list,
            annual_income=profile.annual_income,
            irrigation_type=profile.irrigation_type,
            farming_type=profile.farming_type,
            additional_info=profile.additional_info,
            updated_at=profile.updated_at
        )


profile_service = ProfileService()
