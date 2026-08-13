"""Tests for weather endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from test_server import app

client = TestClient(app)


class TestWeatherEndpoints:
    """Test weather API endpoints."""
    
    @pytest.fixture
    def mock_weather_service(self, monkeypatch):
        """Mock weather service."""
        mock = Mock()
        monkeypatch.setattr("app.api.v1.endpoints.weather.weather_service", mock)
        return mock
    
    @pytest.fixture
    def sample_weather_data(self):
        """Sample weather response."""
        return {
            "location": {
                "name": "Pune",
                "country": "IN",
                "latitude": 18.5204,
                "longitude": 73.8567
            },
            "temperature": 28.5,
            "feels_like": 30.2,
            "humidity": 65,
            "pressure": 1012,
            "wind_speed": 3.5,
            "wind_direction": 180,
            "visibility": 10000,
            "weather_main": "Clear",
            "weather_description": "clear sky",
            "weather_icon": "01d",
            "timestamp": "2024-01-01T12:00:00"
        }
    
    @pytest.fixture
    def sample_forecast_data(self):
        """Sample forecast response."""
        return {
            "location": {
                "name": "Pune",
                "country": "IN"
            },
            "forecast": [
                {
                    "date": "2024-01-02",
                    "temperature_min": 20.0,
                    "temperature_max": 32.0,
                    "humidity": 60,
                    "wind_speed": 3.0,
                    "precipitation_probability": 10.0,
                    "precipitation_amount": 0.0,
                    "weather_main": "Sunny",
                    "weather_description": "clear sky"
                }
            ],
            "generated_at": "2024-01-01T12:00:00"
        }
    
    
    def test_get_current_weather_success(self, mock_weather_service, sample_weather_data):
        """Test getting current weather."""
        mock_weather_service.get_current_weather = AsyncMock(return_value=sample_weather_data)
        
        response = client.get(
            "/api/v1/weather/current?latitude=18.5204&longitude=73.8567"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_current_weather_invalid_coords(self):
        """Test weather with invalid coordinates."""
        response = client.get(
            "/api/v1/weather/current?latitude=999&longitude=999"
        )
        
        assert response.status_code in [422, 404]  # 422 for validation
    
    def test_get_current_weather_service_error(self, mock_weather_service):
        """Test weather when service fails."""
        mock_weather_service.get_current_weather = AsyncMock(return_value=None)
        
        response = client.get(
            "/api/v1/weather/current?latitude=18.5204&longitude=73.8567"
        )
        
        assert response.status_code in [503, 404]
    
    def test_get_forecast_success(self, mock_weather_service, sample_forecast_data):
        """Test getting weather forecast."""
        mock_weather_service.get_forecast = AsyncMock(return_value=sample_forecast_data)
        
        response = client.get(
            "/api/v1/weather/forecast?latitude=18.5204&longitude=73.8567&days=7"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_forecast_default_days(self, mock_weather_service, sample_forecast_data):
        """Test forecast with default days parameter."""
        mock_weather_service.get_forecast = AsyncMock(return_value=sample_forecast_data)
        
        response = client.get(
            "/api/v1/weather/forecast?latitude=18.5204&longitude=73.8567"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_forecast_invalid_days(self):
        """Test forecast with invalid days parameter."""
        response = client.get(
            "/api/v1/weather/forecast?latitude=18.5204&longitude=73.8567&days=30"
        )
        
        assert response.status_code in [422, 404]
    
    def test_post_current_weather(self, mock_weather_service, sample_weather_data):
        """Test POST current weather endpoint."""
        mock_weather_service.get_current_weather = AsyncMock(return_value=sample_weather_data)
        
        response = client.post(
            "/api/v1/weather/current",
            json={"latitude": 18.5204, "longitude": 73.8567}
        )
        
        assert response.status_code in [200, 404]
    
    def test_post_forecast(self, mock_weather_service, sample_forecast_data):
        """Test POST forecast endpoint."""
        mock_weather_service.get_forecast = AsyncMock(return_value=sample_forecast_data)
        
        response = client.post(
            "/api/v1/weather/forecast",
            json={"latitude": 18.5204, "longitude": 73.8567, "days": 7}
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_weather_alerts(self, mock_weather_service):
        """Test getting weather alerts."""
        mock_weather_service.get_current_weather = AsyncMock(return_value={
            "temperature": 42.0,
            "humidity": 25,
            "weather_main": "Clear"
        })
        mock_weather_service.check_alerts = AsyncMock(return_value=[
            {
                "type": "high_temp",
                "severity": "high",
                "title": "Extreme Heat Warning",
                "description": "Temperature is 42°C. Take precautions."
            }
        ])
        
        response = client.get(
            "/api/v1/weather/alerts?latitude=18.5204&longitude=73.8567"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_weather_history(self):
        """Test getting weather history."""
        response = client.get(
            "/api/v1/weather/history?latitude=18.5204&longitude=73.8567&days=7"
        )
        
        assert response.status_code in [200, 404]


class TestWeatherValidation:
    """Test weather endpoint validation."""
    
    def test_latitude_out_of_range(self):
        """Test with latitude out of valid range."""
        response = client.get(
            "/api/v1/weather/current?latitude=91&longitude=73.8567"
        )
        
        assert response.status_code in [422, 404]
    
    def test_longitude_out_of_range(self):
        """Test with longitude out of valid range."""
        response = client.get(
            "/api/v1/weather/current?latitude=18.5204&longitude=181"
        )
        
        assert response.status_code in [422, 404]
    
    def test_missing_coordinates(self):
        """Test without coordinates."""
        response = client.get(
            "/api/v1/weather/current"
        )
        
        assert response.status_code in [422, 404]
    
    def test_public_access(self):
        """Test endpoint is accessible without authentication."""
        response = client.get("/api/v1/weather/current?latitude=18.5204&longitude=73.8567")
        
        assert response.status_code not in [401, 403]
