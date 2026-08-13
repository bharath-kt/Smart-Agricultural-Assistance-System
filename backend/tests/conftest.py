"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from test_server import app as test_app


@pytest.fixture(scope="session")
def app():
    """Create test app instance."""
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock()
    return db


@pytest.fixture
def mock_weather_service():
    """Mock weather service."""
    with patch("app.api.v1.endpoints.weather.weather_service") as mock:
        yield mock


@pytest.fixture
def mock_market_service():
    """Mock market service."""
    with patch("app.api.v1.endpoints.market.market_service") as mock:
        yield mock


@pytest.fixture
def mock_disease_service():
    """Mock disease service."""
    with patch("app.api.v1.endpoints.disease.disease_service") as mock:
        yield mock


@pytest.fixture
def mock_scheme_service():
    """Mock scheme service."""
    with patch("app.api.v1.endpoints.schemes.scheme_service") as mock:
        yield mock


@pytest.fixture
def sample_weather_data():
    """Sample weather data."""
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
def sample_forecast_data():
    """Sample forecast data."""
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
                "weather_main": "Sunny",
                "weather_description": "clear sky"
            }
        ],
        "generated_at": "2024-01-01T12:00:00"
    }


@pytest.fixture
def sample_market_prices():
    """Sample market prices."""
    return [
        {
            "id": 1,
            "crop_name": "Wheat",
            "variety": "Local",
            "state": "Maharashtra",
            "district": "Pune",
            "market_name": "Pune Market",
            "min_price": 2100.0,
            "max_price": 2300.0,
            "modal_price": 2200.0,
            "arrival_quantity": 150.0,
            "unit": "Quintal",
            "price_date": "2024-01-01",
            "source": "Agmarknet"
        }
    ]


@pytest.fixture
def sample_price_prediction():
    """Sample price prediction."""
    return {
        "crop_name": "Wheat",
        "state": "Maharashtra",
        "district": "Pune",
        "predicted_price": 2250.0,
        "confidence_lower": 2100.0,
        "confidence_upper": 2400.0,
        "confidence_score": 0.85,
        "prediction_for_date": "2024-01-08",
        "prediction_made_at": "2024-01-01T12:00:00"
    }


@pytest.fixture
def sample_disease_detection():
    """Sample disease detection result."""
    return {
        "detected_disease": "Tomato___Early_blight",
        "confidence_score": 0.92,
        "alternative_predictions": [
            {"disease_name": "Tomato___Late_blight", "confidence": 0.05},
            {"disease_name": "Tomato___Leaf_Mold", "confidence": 0.03}
        ],
        "treatment": {
            "organic": "Remove infected leaves, apply copper spray",
            "chemical": "Apply chlorothalonil fungicides",
            "preventive": "Rotate crops, stake plants"
        },
        "detected_at": "2024-01-01T12:00:00"
    }


@pytest.fixture
def sample_schemes():
    """Sample government schemes."""
    return [
        {
            "id": 1,
            "scheme_code": "PM-KISAN",
            "name": "Pradhan Mantri Kisan Samman Nidhi",
            "short_description": "Income support of Rs. 6000 per year",
            "source": "PM-KISAN",
            "ministry": "Ministry of Agriculture",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["All Farmers"],
            "eligible_crops": ["All Crops"],
            "benefit_type": "financial",
            "benefit_amount": "Rs. 6000 per year",
            "application_url": "https://pmkisan.gov.in",
            "helpline_number": "155261",
            "is_active": True
        }
    ]
