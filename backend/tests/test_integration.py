"""Integration tests for the API."""
import pytest


class TestAPIIntegration:
    """Integration tests for the complete API flow."""
    
    def test_api_root_accessible(self, client):
        """Test that API root is accessible."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_v1_test_endpoint(self, client):
        """Test API v1 test endpoint lists all endpoints."""
        response = client.get("/api/v1/test")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0
    
    def test_docs_endpoint(self, client):
        """Test Swagger documentation endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestPublicAPIAccess:
    """Test that API endpoints are publicly accessible."""
    
    def test_endpoints_accessible_without_auth(self, client):
        """Test that feature endpoints do not require authentication."""
        endpoints = [
            "/api/v1/weather/current?latitude=18.5&longitude=73.8",
            "/api/v1/market/prices",
            "/api/v1/disease/diseases",
            "/api/v1/schemes"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code not in [401, 403], f"Endpoint {endpoint} should not require auth"


class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_for_nonexistent_endpoint(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.post("/health")
        assert response.status_code == 405
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/weather/current",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422, 404]


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present."""
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        assert "access-control-allow-origin" in response.headers


class TestResponseFormat:
    """Test API response formats."""
    
    def test_json_content_type(self, client):
        """Test JSON content type for API endpoints."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]
    
    def test_response_structure(self, client):
        """Test consistent response structure."""
        response = client.get("/")
        data = response.json()
        assert isinstance(data, dict)
