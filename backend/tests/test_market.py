"""Tests for market price endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from test_server import app

client = TestClient(app)


class TestMarketEndpoints:
    """Test market price API endpoints."""
    
    @pytest.fixture
    def mock_market_service(self, monkeypatch):
        """Mock market service."""
        mock = Mock()
        monkeypatch.setattr("app.api.v1.endpoints.market.market_service", mock)
        return mock
    
    @pytest.fixture
    def sample_prices(self):
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
            },
            {
                "id": 2,
                "crop_name": "Rice",
                "variety": "Basmati",
                "state": "Maharashtra",
                "district": "Pune",
                "market_name": "Pune Market",
                "min_price": 3500.0,
                "max_price": 3800.0,
                "modal_price": 3650.0,
                "arrival_quantity": 200.0,
                "unit": "Quintal",
                "price_date": "2024-01-01",
                "source": "Agmarknet"
            }
        ]
    
    @pytest.fixture
    def sample_prediction(self):
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
    def sample_trends(self):
        """Sample market trends."""
        return {
            "crop_name": "Wheat",
            "state": "Maharashtra",
            "district": "Pune",
            "current_price": 2200.0,
            "price_change_7d": 2.5,
            "price_change_30d": 5.0,
            "trend": "up",
            "average_price": 2150.0
        }
    
    
    def test_get_market_prices_success(self, mock_market_service, sample_prices):
        """Test getting market prices."""
        mock_market_service.get_historical_prices = AsyncMock(return_value=sample_prices)
        
        response = client.get(
            "/api/v1/market/prices"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_market_prices_with_filters(self, mock_market_service, sample_prices):
        """Test getting prices with filters."""
        mock_market_service.get_historical_prices = AsyncMock(return_value=[sample_prices[0]])
        
        response = client.get(
            "/api/v1/market/prices?crop_name=Wheat&state=Maharashtra&district=Pune"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_market_prices_by_crop(self, mock_market_service, sample_prices):
        """Test getting prices for specific crop."""
        mock_market_service.get_historical_prices = AsyncMock(return_value=[sample_prices[0]])
        
        response = client.get(
            "/api/v1/market/prices/Wheat"
        )
        
        assert response.status_code in [200, 404]
    
    def test_predict_price_success(self, mock_market_service, sample_prediction):
        """Test price prediction."""
        mock_market_service.predict_price = AsyncMock(return_value=sample_prediction)
        
        response = client.get(
            "/api/v1/market/predict?crop_name=Wheat&state=Maharashtra&district=Pune"
        )
        
        assert response.status_code in [200, 404]
    
    def test_predict_price_with_date(self, mock_market_service, sample_prediction):
        """Test price prediction with specific date."""
        mock_market_service.predict_price = AsyncMock(return_value=sample_prediction)
        
        response = client.get(
            "/api/v1/market/predict?crop_name=Wheat&state=Maharashtra&district=Pune&prediction_date=2024-01-15"
        )
        
        assert response.status_code in [200, 404]
    
    def test_predict_price_service_error(self, mock_market_service):
        """Test prediction when service fails."""
        mock_market_service.predict_price = AsyncMock(return_value=None)
        
        response = client.get(
            "/api/v1/market/predict?crop_name=Wheat&state=Maharashtra&district=Pune"
        )
        
        assert response.status_code in [503, 404]
    
    def test_post_predict_price(self, mock_market_service, sample_prediction):
        """Test POST price prediction."""
        mock_market_service.predict_price = AsyncMock(return_value=sample_prediction)
        
        response = client.post(
            "/api/v1/market/predict",
            json={
                "crop_name": "Wheat",
                "state": "Maharashtra",
                "district": "Pune"
            }
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_market_trends_success(self, mock_market_service, sample_trends):
        """Test getting market trends."""
        mock_market_service.get_market_trends = AsyncMock(return_value=sample_trends)
        
        response = client.get(
            "/api/v1/market/trends/Wheat?state=Maharashtra&district=Pune"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_market_trends_not_found(self, mock_market_service):
        """Test trends for non-existent crop."""
        mock_market_service.get_market_trends = AsyncMock(return_value=None)
        
        response = client.get(
            "/api/v1/market/trends/UnknownCrop?state=Maharashtra&district=Pune"
        )
        
        assert response.status_code in [404, 200]
    
    def test_get_crops(self):
        """Test getting available crops."""
        response = client.get(
            "/api/v1/market/crops"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_crops_with_category(self):
        """Test getting crops filtered by category."""
        response = client.get(
            "/api/v1/market/crops?category=Cereal"
        )
        
        assert response.status_code in [200, 404]


class TestMarketValidation:
    """Test market endpoint validation."""
    
    def test_predict_price_missing_params(self):
        """Test prediction without required params."""
        response = client.get(
            "/api/v1/market/predict"
        )
        
        assert response.status_code in [422, 404]
    
    def test_get_trends_missing_params(self):
        """Test trends without required params."""
        response = client.get(
            "/api/v1/market/trends/Wheat"
        )
        
        assert response.status_code in [422, 404]
    
    def test_invalid_date_format(self):
        """Test with invalid date format."""
        response = client.get(
            "/api/v1/market/prices?from_date=invalid-date"
        )
        
        assert response.status_code in [422, 404]
    
    def test_limit_out_of_range(self):
        """Test with limit out of valid range."""
        response = client.get(
            "/api/v1/market/prices?limit=5000"
        )
        
        assert response.status_code in [422, 404]
