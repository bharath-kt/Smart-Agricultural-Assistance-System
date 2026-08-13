"""Pydantic schemas for Authentication and Farmer Profile."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    identifier: str = Field(..., description="Email address or 10-digit mobile number")
    password: str = Field(..., min_length=6)
    state: Optional[str] = "Karnataka"
    district: Optional[str] = "Mysuru"
    farmer_category: Optional[str] = "Small"
    land_size: Optional[float] = 1.5
    crops_grown: Optional[List[str]] = ["Tomato", "Paddy"]


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email address or 10-digit mobile number")
    password: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    farmer_category: Optional[str] = None
    land_ownership: Optional[str] = None
    land_size: Optional[float] = None
    crops_grown: Optional[List[str]] = None
    annual_income: Optional[float] = None
    irrigation_type: Optional[str] = None
    farming_type: Optional[str] = None
    additional_info: Optional[str] = None


class ProfileResponse(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    farmer_category: Optional[str] = None
    land_ownership: Optional[str] = None
    land_size: Optional[float] = None
    crops_grown: List[str] = []
    annual_income: Optional[float] = None
    irrigation_type: Optional[str] = None
    farming_type: Optional[str] = None
    additional_info: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    is_active: bool = True
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True
