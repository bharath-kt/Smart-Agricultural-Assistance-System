"""Weather API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_optional_current_user
from app.services.weather_service import weather_service
from app.schemas.weather import (
    CurrentWeatherResponse,
    ForecastRequest,
    ForecastResponse,
    WeatherLocation,
    WeatherAlertResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/weather", tags=["Weather"])


class SearchQuery(BaseModel):
    """Search query for weather by city/pincode."""
    query: str
    days: int = 5


class GeocodeResponse(BaseModel):
    """Geocoding response."""
    name: str
    lat: float
    lon: float
    country: str
    state: Optional[str] = None


class CombinedWeatherResponse(BaseModel):
    """Combined current weather and forecast response."""
    location: dict
    current: dict
    forecast: dict


@router.get("/geocode", response_model=List[GeocodeResponse])
async def geocode_location(
    q: str = Query(..., description="City name or pincode to search"),
):
    """Geocode a city name or pincode to coordinates."""
    result = await weather_service.geocode_location(q)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{q}' not found. Try a different city name or pincode."
        )
    return [GeocodeResponse(**result)]


@router.get("/search", response_model=CombinedWeatherResponse)
async def search_weather(
    q: Optional[str] = Query(None, description="City name or pincode"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    days: int = Query(default=5, ge=1, le=7, description="Forecast days"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search weather by city name/pincode OR by GPS lat/lon. Returns current + forecast."""
    logger.info(f"Weather search request - q: {q}, lat: {lat}, lon: {lon}")
    
    if lat is not None and lon is not None:
        geocode_result = await weather_service.reverse_geocode(lat, lon)
        location_name = geocode_result.get("name") if geocode_result else f"GPS ({lat:.2f}, {lon:.2f})"
    elif q:
        geocode_result = await weather_service.geocode_location(q)
        if not geocode_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location '{q}' not found. Try a different city name or pincode."
            )
        lat = geocode_result["lat"]
        lon = geocode_result["lon"]
        location_name = geocode_result["name"]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either city name 'q' or 'lat' and 'lon' coordinates must be provided."
        )
    
    current = await weather_service.get_current_weather(lat, lon, location_name)
    forecast = await weather_service.get_forecast(lat, lon, days, location_name)
    
    if not current:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch current weather data"
        )
    
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch forecast data"
        )
    
    if current_user:
        try:
            from app.services.history_service import history_service
            temp = current.get("temperature")
            humidity = current.get("humidity")
            cond = current.get("condition") or current.get("weather_description")
            await history_service.log_weather_view(
                db=db,
                user_id=current_user.id,
                location=location_name,
                temp=float(temp) if temp is not None else None,
                humidity=int(humidity) if humidity is not None else None,
                condition=str(cond) if cond else None
            )
        except Exception as e:
            logger.warning(f"Failed to log weather history: {e}")

    return CombinedWeatherResponse(
        location=current["location"],
        current=current,
        forecast=forecast
    )


@router.post("/search", response_model=CombinedWeatherResponse)
async def search_weather_post(
    request: SearchQuery,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search weather by city name or pincode (POST)."""
    return await search_weather(request.query, request.days, current_user=current_user, db=db)


@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """Get current weather for a location by coordinates."""
    weather = await weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    return weather


@router.post("/current", response_model=CurrentWeatherResponse)
async def get_current_weather_post(location: WeatherLocation):
    """Get current weather for a location (POST method)."""
    weather = await weather_service.get_current_weather(
        location.latitude, 
        location.longitude
    )
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    return weather


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(default=7, ge=1, le=16, description="Number of days"),
):
    """Get weather forecast for a location by coordinates."""
    forecast = await weather_service.get_forecast(latitude, longitude, days)
    
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch forecast data"
        )
    
    return forecast


@router.post("/forecast", response_model=ForecastResponse)
async def get_forecast_post(request: ForecastRequest):
    """Get weather forecast for a location (POST method)."""
    forecast = await weather_service.get_forecast(
        request.latitude,
        request.longitude,
        request.days
    )
    
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch forecast data"
        )
    
    return forecast


@router.get("/alerts", response_model=List[WeatherAlertResponse])
async def get_weather_alerts(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    db: AsyncSession = Depends(get_db)
):
    """Get weather alerts for a location."""
    weather = await weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    alerts = await weather_service.check_alerts(latitude, longitude, weather)
    
    return alerts


@router.get("/history", response_model=List[dict])
async def get_weather_history(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get historical weather data for a location."""
    from sqlalchemy import select
    from app.models.weather import WeatherHistory
    from datetime import datetime, timedelta
    
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(WeatherHistory)
        .where(
            WeatherHistory.latitude == latitude,
            WeatherHistory.longitude == longitude,
            WeatherHistory.recorded_at >= since
        )
        .order_by(WeatherHistory.recorded_at.desc())
    )
    
    history = result.scalars().all()
    return history
