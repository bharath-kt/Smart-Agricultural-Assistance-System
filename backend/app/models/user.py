"""User model definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class UserType(str, enum.Enum):
    """User type enumeration."""
    FARMER = "farmer"
    TRADER = "trader"
    ADMIN = "admin"


class AuthMethod(str, enum.Enum):
    """Authentication method enumeration."""
    MOBILE_OTP = "mobile_otp"
    MOBILE_PASSWORD = "mobile_password"
    EMAIL = "email"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(20), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    user_type = Column(Enum(UserType), default=UserType.FARMER)
    auth_method = Column(Enum(AuthMethod), nullable=True)
    
    # Profile fields
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    preferred_crops = Column(String(500), nullable=True)  # Comma-separated
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    otp_records = relationship("OTPRecord", back_populates="user", cascade="all, delete-orphan")
    weather_alerts = relationship("WeatherAlert", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class FarmerProfile(Base):
    """Detailed farmer profile model."""
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    full_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # Male, Female, Other
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    farmer_category = Column(String(50), nullable=True)  # Small, Marginal, Medium, Large
    land_ownership = Column(String(50), nullable=True)  # Owned, Leased, Joint
    land_size = Column(Float, nullable=True)  # in hectares
    crops_grown = Column(String(1000), nullable=True)  # JSON list string
    annual_income = Column(Float, nullable=True)
    irrigation_type = Column(String(100), nullable=True)  # Rainfed, Well, Canal, Drip, Sprinkler
    farming_type = Column(String(100), nullable=True)  # Organic, Conventional, Mixed
    additional_info = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class OTPRecord(Base):
    """OTP record model for verification."""
    __tablename__ = "otp_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    mobile_number = Column(String(20), index=True)
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(50), default="login")  # login, registration, password_reset
    
    # Tracking
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    is_verified = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="otp_records")


class RefreshToken(Base):
    """Refresh token model."""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
