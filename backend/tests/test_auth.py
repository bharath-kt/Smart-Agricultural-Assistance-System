"""Tests for farmer authentication, profile persistence, and data isolation."""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client with FastAPI lifespan event context so database tables are initialized."""
    with TestClient(app) as c:
        yield c


class TestFarmerAuthAndProfile:
    """Test suite for farmer registration, login, profile, and history isolation."""

    def test_signup_email_success(self, client):
        """Test registration using an email address."""
        uid = str(uuid.uuid4())[:8]
        email = f"ramesh_{uid}@example.com"
        payload = {
            "full_name": "Ramesh Gowda",
            "identifier": email,
            "password": "password123",
            "state": "Karnataka",
            "district": "Mysuru",
            "farmer_category": "Small",
            "land_size": 1.8,
            "crops_grown": ["Tomato", "Paddy"]
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["full_name"] == "Ramesh Gowda"

    def test_signup_register_alias(self, client):
        """Test registration using the /register alias endpoint."""
        uid = str(uuid.uuid4())[:8]
        email = f"suresh_{uid}@example.com"
        payload = {
            "full_name": "Suresh Patel",
            "identifier": email,
            "password": "password123",
            "state": "Gujarat",
            "district": "Anand",
            "farmer_category": "Medium",
            "land_size": 3.5,
            "crops_grown": ["Cotton", "Wheat"]
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data

    def test_signup_mobile_success(self, client):
        """Test registration using a 10-digit mobile number."""
        import random
        mobile = f"9{random.randint(100000000, 999999999)}"
        payload = {
            "full_name": "Lakshmi Devi",
            "identifier": mobile,
            "password": "securepassword",
            "state": "Karnataka",
            "district": "Mandya",
            "farmer_category": "Marginal",
            "land_size": 0.8,
            "crops_grown": ["Paddy", "Sugarcane"]
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data

    def test_signup_duplicate_error(self, client):
        """Test registering with an already existing email."""
        uid = str(uuid.uuid4())[:8]
        email = f"dup_{uid}@example.com"
        payload = {
            "full_name": "Original Farmer",
            "identifier": email,
            "password": "password123",
            "state": "Karnataka",
            "district": "Mysuru"
        }
        res1 = client.post("/api/v1/auth/signup", json=payload)
        assert res1.status_code == 201

        res2 = client.post("/api/v1/auth/signup", json=payload)
        assert res2.status_code == 400
        assert "already exists" in res2.json()["detail"]

    def test_login_email_success(self, client):
        """Test login with email and valid password."""
        uid = str(uuid.uuid4())[:8]
        email = f"login_{uid}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Login Farmer",
            "identifier": email,
            "password": "password123"
        })

        payload = {
            "identifier": email,
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["full_name"] == "Login Farmer"

    def test_login_mobile_success(self, client):
        """Test login with mobile number and valid password."""
        import random
        mobile = f"9{random.randint(100000000, 999999999)}"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Mobile Farmer",
            "identifier": mobile,
            "password": "securepassword"
        })

        payload = {
            "identifier": mobile,
            "password": "securepassword"
        }
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        """Test login failure with incorrect password."""
        uid = str(uuid.uuid4())[:8]
        email = f"wrong_{uid}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Test User",
            "identifier": email,
            "password": "correctpassword"
        })

        payload = {
            "identifier": email,
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401

    def test_get_me_profile(self, client):
        """Test loading registered farmer details via /auth/me."""
        uid = str(uuid.uuid4())[:8]
        email = f"me_{uid}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Ramesh Gowda",
            "identifier": email,
            "password": "password123",
            "state": "Karnataka",
            "district": "Mysuru",
            "farmer_category": "Small",
            "land_size": 1.8,
            "crops_grown": ["Tomato", "Paddy"]
        })

        login_resp = client.post("/api/v1/auth/login", json={
            "identifier": email,
            "password": "password123"
        })
        token = login_resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        me_resp = client.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["full_name"] == "Ramesh Gowda"
        assert me_data["email"] == email
        assert me_data["profile"]["state"] == "Karnataka"
        assert me_data["profile"]["district"] == "Mysuru"
        assert me_data["profile"]["farmer_category"] == "Small"
        assert me_data["profile"]["land_size"] == 1.8
        assert "Tomato" in me_data["profile"]["crops_grown"]

    def test_update_profile(self, client):
        """Test updating farmer profile."""
        uid = str(uuid.uuid4())[:8]
        email = f"update_{uid}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Update Farmer",
            "identifier": email,
            "password": "password123"
        })

        login_resp = client.post("/api/v1/auth/login", json={
            "identifier": email,
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        update_payload = {
            "district": "Hassan",
            "land_size": 2.2,
            "crops_grown": ["Tomato", "Chilli", "Corn"]
        }
        put_resp = client.put("/api/v1/profile", json=update_payload, headers=headers)
        assert put_resp.status_code == 200
        updated = put_resp.json()
        assert updated["district"] == "Hassan"
        assert updated["land_size"] == 2.2
        assert "Chilli" in updated["crops_grown"]

    def test_personalized_recommendations(self, client):
        """Test scheme recommendations personalized to farmer profile."""
        uid = str(uuid.uuid4())[:8]
        email = f"rec_{uid}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Rec Farmer",
            "identifier": email,
            "password": "password123",
            "state": "Karnataka",
            "district": "Mysuru"
        })

        login_resp = client.post("/api/v1/auth/login", json={
            "identifier": email,
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        rec_resp = client.get("/api/v1/schemes/recommendations", headers=headers)
        assert rec_resp.status_code == 200
        rec_data = rec_resp.json()
        assert "recommendations" in rec_data
        assert "eligible_count" in rec_data

    def test_farmer_isolation(self, client):
        """Ensure Farmer A cannot view or alter Farmer B's profile or history."""
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"farmer_a_{uid_a}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Farmer A",
            "identifier": email_a,
            "password": "password123"
        })

        uid_b = str(uuid.uuid4())[:8]
        email_b = f"farmer_b_{uid_b}@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "Farmer B",
            "identifier": email_b,
            "password": "password123"
        })

        login_a = client.post("/api/v1/auth/login", json={"identifier": email_a, "password": "password123"})
        token_a = login_a.json()["access_token"]

        login_b = client.post("/api/v1/auth/login", json={"identifier": email_b, "password": "password123"})
        token_b = login_b.json()["access_token"]

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        profile_a = client.get("/api/v1/profile", headers=headers_a).json()
        profile_b = client.get("/api/v1/profile", headers=headers_b).json()

        assert profile_a["user_id"] != profile_b["user_id"]
        assert profile_a["full_name"] == "Farmer A"
        assert profile_b["full_name"] == "Farmer B"

        # Farmer A searches weather
        client.get("/api/v1/weather/search?q=Mysuru", headers=headers_a)

        hist_a = client.get("/api/v1/history/all", headers=headers_a).json()
        hist_b = client.get("/api/v1/history/all", headers=headers_b).json()

        assert hist_a["farmer_id"] != hist_b["farmer_id"]
        for item in hist_b["weather_history"]:
            assert item["location_name"] != "Mysuru"
