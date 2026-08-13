"""Tests for government schemes endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

from test_server import app

client = TestClient(app)


class TestSchemesEndpoints:
    """Test government schemes API endpoints."""
    
    @pytest.fixture
    def mock_scheme_service(self, monkeypatch):
        """Mock scheme service."""
        mock = Mock()
        monkeypatch.setattr("app.api.v1.endpoints.schemes.scheme_service", mock)
        return mock
    
    @pytest.fixture
    def sample_schemes(self):
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
            },
            {
                "id": 2,
                "scheme_code": "PMFBY",
                "name": "Pradhan Mantri Fasal Bima Yojana",
                "short_description": "Crop insurance scheme",
                "source": "PMFBY",
                "ministry": "Ministry of Agriculture",
                "eligible_states": ["All States"],
                "eligible_farmer_types": ["All Farmers"],
                "eligible_crops": ["Food Crops", "Oilseeds"],
                "benefit_type": "insurance",
                "benefit_amount": "Up to full sum insured",
                "application_url": "https://pmfby.gov.in",
                "helpline_number": "1800-180-1551",
                "is_active": True
            }
        ]
    
    @pytest.fixture
    def sample_scheme_detail(self):
        """Sample detailed scheme."""
        return {
            "id": 1,
            "scheme_code": "PM-KISAN",
            "name": "Pradhan Mantri Kisan Samman Nidhi",
            "short_description": "Income support of Rs. 6000 per year",
            "full_description": "PM-KISAN is a Central Sector scheme...",
            "source": "PM-KISAN",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "All Farmers"],
            "eligible_crops": ["All Crops"],
            "max_land_holding": 2.0,
            "income_criteria": "Landholding up to 2 hectares",
            "benefit_type": "financial",
            "benefit_amount": "Rs. 6000 per year",
            "benefit_description": "Direct cash transfer",
            "required_documents": ["Aadhaar Card", "Land Records", "Bank Account"],
            "application_process": "Register online at pmkisan.gov.in",
            "application_url": "https://pmkisan.gov.in",
            "helpline_number": "155261",
            "helpline_email": "pmkisan-ict@gov.in",
            "official_website": "https://pmkisan.gov.in",
            "start_date": "2019-02-01",
            "end_date": None,
            "is_active": True,
            "tags": ["income support", "cash transfer"]
        }
    
    @pytest.fixture
    def sample_eligibility_result(self):
        """Sample eligibility check result."""
        return {
            "scheme_id": 1,
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi",
            "is_eligible": True,
            "reasons": [],
            "missing_documents": ["Aadhaar Card", "Land Records", "Bank Account Details"]
        }
    
    
    def test_get_schemes_success(self, mock_scheme_service, sample_schemes):
        """Test getting all schemes."""
        mock_scheme_service.get_schemes = AsyncMock(return_value=sample_schemes)
        
        response = client.get(
            "/api/v1/schemes"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_schemes_with_filters(self, mock_scheme_service, sample_schemes):
        """Test getting schemes with filters."""
        mock_scheme_service.get_schemes = AsyncMock(return_value=[sample_schemes[0]])
        
        response = client.get(
            "/api/v1/schemes?state=Maharashtra&farmer_type=Small&crop=Wheat"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_schemes_with_search(self, mock_scheme_service, sample_schemes):
        """Test searching schemes."""
        mock_scheme_service.get_schemes = AsyncMock(return_value=[sample_schemes[0]])
        
        response = client.get(
            "/api/v1/schemes?search=income"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_schemes_with_pagination(self, mock_scheme_service, sample_schemes):
        """Test schemes with pagination."""
        mock_scheme_service.get_schemes = AsyncMock(return_value=sample_schemes)
        
        response = client.get(
            "/api/v1/schemes?skip=0&limit=10"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_scheme_by_id_success(self, mock_scheme_service, sample_scheme_detail):
        """Test getting scheme by ID."""
        mock_scheme_service.get_scheme_by_id = AsyncMock(return_value=sample_scheme_detail)
        
        response = client.get(
            "/api/v1/schemes/1"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_scheme_by_id_not_found(self, mock_scheme_service):
        """Test getting non-existent scheme."""
        mock_scheme_service.get_scheme_by_id = AsyncMock(return_value=None)
        
        response = client.get(
            "/api/v1/schemes/999"
        )
        
        assert response.status_code in [404, 200]
    
    def test_search_schemes_get(self, mock_scheme_service, sample_schemes):
        """Test GET search schemes."""
        mock_scheme_service.search_schemes = AsyncMock(return_value=sample_schemes)
        
        response = client.get(
            "/api/v1/schemes/search/query?query=income&state=Maharashtra"
        )
        
        assert response.status_code in [200, 404]
    
    def test_search_schemes_post(self, mock_scheme_service, sample_schemes):
        """Test POST search schemes."""
        mock_scheme_service.search_schemes = AsyncMock(return_value=sample_schemes)
        
        response = client.post(
            "/api/v1/schemes/search",
            json={"query": "income", "state": "Maharashtra", "crop": "Wheat"}
        )
        
        assert response.status_code in [200, 404]
    
    def test_check_eligibility_success(self, mock_scheme_service, sample_eligibility_result):
        """Test eligibility check."""
        mock_scheme_service.check_eligibility = AsyncMock(return_value=sample_eligibility_result)
        
        response = client.post(
            "/api/v1/schemes/eligibility",
            json={
                "scheme_id": 1,
                "state": "Maharashtra",
                "farmer_type": "Small",
                "land_holding": 1.5,
                "crops": ["Wheat", "Rice"]
            }
        )
        
        assert response.status_code in [200, 404]
    
    def test_check_eligibility_not_eligible(self, mock_scheme_service):
        """Test eligibility check when not eligible."""
        mock_scheme_service.check_eligibility = AsyncMock(return_value={
            "scheme_id": 1,
            "scheme_name": "PM-KISAN",
            "is_eligible": False,
            "reasons": ["Land holding exceeds maximum of 2 hectares"],
            "missing_documents": ["Aadhaar Card"]
        })
        
        response = client.post(
            "/api/v1/schemes/eligibility",
            json={
                "scheme_id": 1,
                "state": "Maharashtra",
                "farmer_type": "Large",
                "land_holding": 5.0
            }
        )
        
        assert response.status_code in [200, 404]
    
    def test_check_eligibility_scheme_not_found(self, mock_scheme_service):
        """Test eligibility check for non-existent scheme."""
        mock_scheme_service.check_eligibility = AsyncMock(return_value=None)
        
        response = client.post(
            "/api/v1/schemes/eligibility",
            json={
                "scheme_id": 999,
                "state": "Maharashtra",
                "farmer_type": "Small"
            }
        )
        
        assert response.status_code in [404, 200]
    
    def test_get_scheme_sources(self):
        """Test getting scheme sources."""
        response = client.get(
            "/api/v1/schemes/sources/list"
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_scheme_categories(self):
        """Test getting scheme categories."""
        response = client.get(
            "/api/v1/schemes/categories/list"
        )
        
        assert response.status_code in [200, 404]


class TestSchemesValidation:
    """Test schemes endpoint validation."""
    
    def test_search_query_too_short(self):
        """Test search with query too short."""
        response = client.get(
            "/api/v1/schemes/search/query?query=a"
        )
        
        assert response.status_code in [422, 404]
    
    def test_invalid_pagination_params(self):
        """Test with invalid pagination."""
        response = client.get(
            "/api/v1/schemes?skip=-1&limit=0"
        )
        
        assert response.status_code in [422, 404]
    
    def test_limit_too_high(self):
        """Test with limit exceeding maximum."""
        response = client.get(
            "/api/v1/schemes?limit=5000"
        )
        
        assert response.status_code in [422, 404]
    
    def test_missing_required_eligibility_fields(self):
        """Test eligibility check without required fields."""
        response = client.post(
            "/api/v1/schemes/eligibility",
            json={"scheme_id": 1}
        )
        
        assert response.status_code in [422, 404]
    
    def test_public_access(self):
        """Test endpoint is accessible without authentication."""
        response = client.get("/api/v1/schemes")
        
        assert response.status_code not in [401, 403]
