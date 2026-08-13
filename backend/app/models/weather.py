"""Weather model definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class WeatherHistory(Base):
    """Weather history model."""
    __tablename__ = "weather_history"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    location_name = Column(String(255), nullable=True)
    
    # Current weather data
    temperature = Column(Float, nullable=True)
    feels_like = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)
    pressure = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Integer, nullable=True)
    visibility = Column(Integer, nullable=True)
    
    # Weather condition
    weather_main = Column(String(100), nullable=True)
    weather_description = Column(String(255), nullable=True)
    weather_icon = Column(String(50), nullable=True)
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)
    api_timestamp = Column(DateTime, nullable=True)


class WeatherForecast(Base):
    """Weather forecast model."""
    __tablename__ = "weather_forecast"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Forecast data
    forecast_date = Column(DateTime, nullable=False, index=True)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    precipitation_probability = Column(Float, nullable=True)
    precipitation_amount = Column(Float, nullable=True)
    
    # Weather condition
    weather_main = Column(String(100), nullable=True)
    weather_description = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class WeatherAlert(Base):
    """Weather alert model."""
    __tablename__ = "weather_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # rain, drought, high_temp, frost
    severity = Column(String(20), nullable=False)  # low, medium, high
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="weather_alerts")
