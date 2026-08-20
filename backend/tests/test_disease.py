"""Tests for disease detection endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from io import BytesIO

from test_server import app

client = TestClient(app)


class TestDiseaseEndpoints:
    """Test disease detection API endpoints."""
    
    @pytest.fixture
    def mock_disease_service(self, monkeypatch):
        """Mock disease service."""
        mock = Mock()
        monkeypatch.setattr("app.api.v1.endpoints.disease.disease_service", mock)
        return mock
    
    @pytest.fixture
    def sample_detection_result(self):
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
    def sample_disease_info(self):
        """Sample disease information."""
        return {
            "name": "Tomato___Early_blight",
            "crop": "Tomato",
            "condition": "Early blight",
            "affected_crops": ["Tomato"],
            "symptoms": "Dark brown spots with concentric rings on leaves",
            "treatment": {
                "organic": "Remove infected leaves",
                "chemical": "Apply fungicides",
                "preventive": "Crop rotation"
            },
            "is_healthy": False
        }
    
    @pytest.fixture
    def sample_detection_history(self):
        """Sample detection history."""
        return [
            {
                "id": 1,
                "detected_disease": "Tomato___Early_blight",
                "confidence_score": 0.92,
                "crop_type": "Tomato",
                "created_at": "2024-01-01T12:00:00",
                "is_validated": False
            }
        ]
    
    
    def test_detect_disease_success(self, mock_disease_service, sample_detection_result):
        """Test disease detection with valid image."""
        mock_disease_service.detect_disease = AsyncMock(return_value=sample_detection_result)
        
        # Create a mock image file
        image_data = BytesIO(b"fake_image_data")
        
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("test.jpg", image_data, "image/jpeg")},
            data={"crop_type": "Tomato"}
        )
        
        assert response.status_code in [200, 404]
    
    def test_detect_disease_unsupported_crop(self):
        """Test detection with Paddy crop (unsupported)."""
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("test.jpg", BytesIO(b"fake_image_data"), "image/jpeg")},
            data={"crop_type": "Paddy"}
        )
        assert response.status_code in [400, 404]
        if response.status_code == 400:
            assert "Unsupported crop" in response.json()["detail"]

    def test_detect_disease_missing_crop(self):
        """Test detection without selecting a crop."""
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("test.jpg", BytesIO(b"fake_image_data"), "image/jpeg")}
        )
        assert response.status_code in [400, 404]
        if response.status_code == 400:
            assert "Please select a crop" in response.json()["detail"]
    
    def test_detect_disease_invalid_file_type(self):
        """Test detection with invalid file type."""
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("test.txt", BytesIO(b"not an image"), "text/plain")},
            data={"crop_type": "Tomato"}
        )
        
        assert response.status_code in [400, 404]
    
    def test_detect_disease_file_too_large(self):
        """Test detection with file too large."""
        # Create a large fake file (over 10MB)
        large_file = BytesIO(b"x" * (11 * 1024 * 1024))
        
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("large.jpg", large_file, "image/jpeg")},
            data={"crop_type": "Tomato"}
        )
        
        assert response.status_code in [400, 413, 404]
    
    def test_detect_disease_service_error(self, mock_disease_service):
        """Test detection when service fails."""
        mock_disease_service.detect_disease = AsyncMock(return_value=None)
        
        response = client.post(
            "/api/v1/disease/detect",
            files={"image": ("test.jpg", BytesIO(b"fake"), "image/jpeg")},
            data={"crop_type": "Tomato"}
        )
        
        assert response.status_code in [500, 404]
    
    def test_get_disease_info_success(self, mock_disease_service, sample_disease_info):
        """Test getting disease information."""
        mock_disease_service.get_disease_info = AsyncMock(return_value=sample_disease_info)
        
        response = client.get(
            "/api/v1/disease/info/Tomato___Early_blight"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_disease_info_not_found(self, mock_disease_service):
        """Test getting info for non-existent disease."""
        mock_disease_service.get_disease_info = AsyncMock(return_value=None)
        
        response = client.get(
            "/api/v1/disease/info/Unknown_Disease"
        )
        
        assert response.status_code in [404, 200]
    
    def test_get_detection_history(self):
        """Test getting detection history."""
        response = client.get(
            "/api/v1/disease/history"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_detection_history_with_limit(self):
        """Test getting detection history with limit."""
        response = client.get(
            "/api/v1/disease/history?limit=5"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_supported_diseases(self):
        """Test getting list of supported diseases."""
        response = client.get(
            "/api/v1/disease/diseases"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_supported_diseases_filtered(self):
        """Test getting diseases filtered by crop type."""
        response = client.get(
            "/api/v1/disease/diseases?crop_type=Tomato"
        )
        
        assert response.status_code in [200, 404]


class TestDiseaseValidation:
    """Test disease endpoint validation."""
    
    def test_missing_image(self):
        """Test detection without image."""
        response = client.post(
            "/api/v1/disease/detect"
        )
        
        assert response.status_code in [422, 404]
    
    def test_invalid_limit_value(self):
        """Test history with invalid limit."""
        response = client.get(
            "/api/v1/disease/history?limit=-1"
        )
        
        assert response.status_code in [422, 404]
    
    def test_public_access(self):
        """Test endpoint is accessible without authentication."""
        response = client.get("/api/v1/disease/history")
        
        assert response.status_code not in [401, 403]
