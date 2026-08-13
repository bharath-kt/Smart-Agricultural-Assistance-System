"""Weather Pydantic schemas."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherLocation(BaseModel):
    """Weather location schema."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class CurrentWeatherRequest(WeatherLocation):
    """Current weather request schema."""
    pass


class CurrentWeatherResponse(BaseModel):
    """Current weather response schema."""
    location: dict
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: Optional[int]
    visibility: Optional[int]
    weather_main: str
    weather_description: str
    weather_icon: Optional[str]
    timestamp: datetime


class ForecastRequest(WeatherLocation):
    """Forecast request schema."""
    days: int = Field(default=7, ge=1, le=16)


class DailyForecast(BaseModel):
    """Daily forecast schema."""
    date: date
    temperature_min: float
    temperature_max: float
    humidity: int
    wind_speed: float
    precipitation_probability: Optional[float]
    precipitation_amount: Optional[float]
    weather_main: str
    weather_description: str


class ForecastResponse(BaseModel):
    """Forecast response schema."""
    location: dict
    forecast: List[DailyForecast]
    generated_at: datetime


class WeatherAlertCreate(BaseModel):
    """Weather alert creation schema."""
    user_id: int
    alert_type: str = Field(..., pattern=r'^(rain|drought|high_temp|frost|storm)$')
    severity: str = Field(..., pattern=r'^(low|medium|high)$')
    title: str
    description: Optional[str]
    latitude: float
    longitude: float
    expires_at: Optional[datetime]


class WeatherAlertResponse(BaseModel):
    """Weather alert response schema."""
    id: int
    alert_type: str
    severity: str
    title: str
    description: Optional[str]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WeatherHistoryEntry(BaseModel):
    """Weather history entry schema."""
    id: int
    latitude: float
    longitude: float
    location_name: Optional[str]
    temperature: Optional[float]
    humidity: Optional[int]
    weather_main: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True
