"""Farmer activity history models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from app.db.base import Base


class UserWeatherHistory(Base):
    """User weather search/view history model."""
    __tablename__ = "user_weather_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    location_name = Column(String(255), nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)
    weather_condition = Column(String(100), nullable=True)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserMarketHistory(Base):
    """User market price query history model."""
    __tablename__ = "user_market_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    market_name = Column(String(255), nullable=True)
    modal_price = Column(Float, nullable=True)
    trend = Column(String(50), nullable=True)  # Upward, Downward, Stable
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActivityLog(Base):
    """Unified user activity log model."""
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # disease_detection, scheme_search, weather_view, market_query, profile_update
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meta_data = Column(Text, nullable=True)  # JSON metadata string
    created_at = Column(DateTime, default=datetime.utcnow)
