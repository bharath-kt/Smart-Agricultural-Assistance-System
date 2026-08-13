"""Authentication service."""
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status

from app.models.user import User, FarmerProfile, UserType, AuthMethod
from app.models.history import UserActivityLog
from app.schemas.user import SignupRequest, LoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    """Service handling farmer signup, login, and user profile initialization."""

    async def signup(self, db: AsyncSession, request: SignupRequest) -> TokenResponse:
        identifier = request.identifier.strip().lower()
        is_email = "@" in identifier

        # Check if user exists
        if is_email:
            query = select(User).where(User.email == identifier)
        else:
            query = select(User).where(User.mobile_number == identifier)

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or mobile number already exists."
            )

        hashed_pwd = get_password_hash(request.password)

        new_user = User(
            full_name=request.full_name,
            email=identifier if is_email else None,
            mobile_number=identifier if not is_email else None,
            hashed_password=hashed_pwd,
            user_type=UserType.FARMER,
            auth_method=AuthMethod.EMAIL if is_email else AuthMethod.MOBILE_PASSWORD,
            state=request.state,
            district=request.district,
            preferred_crops=",".join(request.crops_grown) if request.crops_grown else "Tomato, Paddy",
            is_active=True,
            is_verified=True
        )
        db.add(new_user)
        await db.flush()

        crops_json = json.dumps(request.crops_grown) if request.crops_grown else json.dumps(["Tomato", "Paddy"])
        farmer_profile = FarmerProfile(
            user_id=new_user.id,
            full_name=request.full_name,
            age=35,
            gender="Male",
            state=request.state or "Karnataka",
            district=request.district or "Mysuru",
            farmer_category=request.farmer_category or "Small",
            land_ownership="Owned",
            land_size=request.land_size if request.land_size is not None else 1.5,
            crops_grown=crops_json,
            annual_income=180000.0,
            irrigation_type="Well",
            farming_type="Conventional"
        )
        db.add(farmer_profile)

        await db.commit()
        await db.refresh(new_user)

        token = create_access_token(data={"sub": str(new_user.id), "name": new_user.full_name})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=new_user.id,
            full_name=new_user.full_name
        )

    async def login(self, db: AsyncSession, request: LoginRequest) -> TokenResponse:
        identifier = request.identifier.strip().lower()

        query = select(User).where(
            or_(
                User.email == identifier,
                User.mobile_number == identifier
            )
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials. Please check your email/mobile and password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )

        token = create_access_token(data={"sub": str(user.id), "name": user.full_name})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            full_name=user.full_name
        )


auth_service = AuthService()
