"""Weather-related background tasks."""
from datetime import datetime
from typing import List, Dict, Any

from app.tasks.celery_app import celery_app
from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.models.weather import WeatherHistory

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def fetch_weather_for_location(self, latitude: float, longitude: float):
    """Fetch and store weather data for a location."""
    try:
        # This would be called with sync client in Celery
        import requests
        from app.core.config import settings
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Store in database
        db = SessionLocal()
        try:
            weather_record = WeatherHistory(
                latitude=latitude,
                longitude=longitude,
                location_name=data.get("name"),
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data.get("wind", {}).get("speed"),
                wind_direction=data.get("wind", {}).get("deg"),
                visibility=data.get("visibility"),
                weather_main=data["weather"][0]["main"],
                weather_description=data["weather"][0]["description"],
                weather_icon=data["weather"][0].get("icon"),
                api_timestamp=datetime.utcfromtimestamp(data["dt"])
            )
            db.add(weather_record)
            db.commit()
            
            logger.info(f"Weather data stored for {latitude}, {longitude}")
            return {"status": "success", "location": f"{latitude}, {longitude}"}
            
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Error fetching weather: {exc}")
        self.retry(exc=exc, countdown=60)


@celery_app.task
def fetch_weather_for_all_locations():
    """Fetch weather for all tracked locations."""
    # Get unique locations from database
    db = SessionLocal()
    try:
        # In production, get locations from user preferences
        # For now, use some default Indian locations
        locations = [
            (28.6139, 77.2090),  # Delhi
            (19.0760, 72.8777),  # Mumbai
            (12.9716, 77.5946),  # Bangalore
            (17.3850, 78.4867),  # Hyderabad
            (22.5726, 88.3639),  # Kolkata
        ]
        
        for lat, lon in locations:
            fetch_weather_for_location.delay(lat, lon)
        
        return {"status": "success", "locations_queued": len(locations)}
        
    finally:
        db.close()


@celery_app.task
def generate_weather_alerts():
    """Generate weather alerts based on conditions."""
    logger.info("Generating weather alerts")
    # Implementation would check weather conditions and create alerts
    return {"status": "success"}
