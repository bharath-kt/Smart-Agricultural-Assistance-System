"""Tests for Farmer History Data Isolation and Delete Operations."""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan context so DB tables are initialized."""
    with TestClient(app) as c:
        yield c


class TestHistoryDataIsolation:
    """Test suite for strict farmer activity history data isolation."""

    def test_farmer_history_isolation_and_delete(self, client):
        """Verify Farmer A and Farmer B history items are strictly isolated and non-cross-accessible."""

        uid_a = str(uuid.uuid4())[:8]
        email_a = f"account_a_{uid_a}@test.com"

        uid_b = str(uuid.uuid4())[:8]
        email_b = f"account_b_{uid_b}@test.com"

        # 1. Signup Farmer A
        signup_a = client.post("/api/v1/auth/signup", json={
            "full_name": "Farmer A",
            "identifier": email_a,
            "password": "Password123!",
            "farmer_category": "Small",
            "state": "Karnataka",
            "district": "Mysuru",
            "land_size": 2.0,
            "crops_grown": ["Rice", "Corn"]
        })
        assert signup_a.status_code in (200, 201), signup_a.text
        token_a = signup_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Signup Farmer B
        signup_b = client.post("/api/v1/auth/signup", json={
            "full_name": "Farmer B",
            "identifier": email_b,
            "password": "Password123!",
            "farmer_category": "Large",
            "state": "Punjab",
            "district": "Ludhiana",
            "land_size": 15.0,
            "crops_grown": ["Wheat", "Cotton"]
        })
        assert signup_b.status_code in (200, 201), signup_b.text
        token_b = signup_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Create activities for Farmer A
        w_a = client.get("/api/v1/weather/search?q=Mysuru", headers=headers_a)
        assert w_a.status_code == 200, w_a.text

        m_a = client.get("/api/v1/market/prices?crop_name=Tomato", headers=headers_a)
        assert m_a.status_code == 200, m_a.text

        s_a = client.get("/api/v1/schemes/recommendations", headers=headers_a)
        assert s_a.status_code == 200, s_a.text

        # 4. Create activities for Farmer B
        w_b = client.get("/api/v1/weather/search?q=Ludhiana", headers=headers_b)
        assert w_b.status_code == 200, w_b.text

        m_b = client.get("/api/v1/market/prices?crop_name=Wheat", headers=headers_b)
        assert m_b.status_code == 200, m_b.text

        s_b = client.get("/api/v1/schemes/recommendations", headers=headers_b)
        assert s_b.status_code == 200, s_b.text

        # 5. Fetch Combined History for Farmer A
        hist_a_res = client.get("/api/v1/history/all", headers=headers_a)
        assert hist_a_res.status_code == 200
        data_a = hist_a_res.json()

        # Verify Farmer A's history contains A's location and crop
        weather_locs_a = [w["location_name"] for w in data_a["weather_history"]]
        market_crops_a = [m["crop_name"] for m in data_a["market_history"]]
        assert "Mysuru" in weather_locs_a
        assert "Ludhiana" not in weather_locs_a
        assert "Tomato" in market_crops_a
        assert "Wheat" not in market_crops_a

        # 6. Fetch Combined History for Farmer B
        hist_b_res = client.get("/api/v1/history/all", headers=headers_b)
        assert hist_b_res.status_code == 200
        data_b = hist_b_res.json()

        # Verify Farmer B's history contains B's location and crop
        weather_locs_b = [w["location_name"] for w in data_b["weather_history"]]
        market_crops_b = [m["crop_name"] for m in data_b["market_history"]]
        assert "Ludhiana" in weather_locs_b
        assert "Mysuru" not in weather_locs_b
        assert "Wheat" in market_crops_b
        assert "Tomato" not in market_crops_b

        # 7. Test cross-farmer DELETE prevention
        item_id_b = data_b["weather_history"][0]["id"]

        # Farmer A attempts to delete Farmer B's weather item
        del_attempt = client.delete(f"/api/v1/history/weather/{item_id_b}", headers=headers_a)
        assert del_attempt.status_code == 404, "Farmer A must NOT be allowed to delete Farmer B's item"

        # Verify Farmer B's item still exists
        hist_b_after = client.get("/api/v1/history/all", headers=headers_b)
        assert item_id_b in [w["id"] for w in hist_b_after.json()["weather_history"]]

        # 8. Test DELETE /api/v1/history/all for Farmer A
        clear_a = client.delete("/api/v1/history/all", headers=headers_a)
        assert clear_a.status_code == 200

        # Verify Farmer A's history is now completely empty
        hist_a_cleared = client.get("/api/v1/history/all", headers=headers_a)
        data_a_cleared = hist_a_cleared.json()
        assert len(data_a_cleared["weather_history"]) == 0
        assert len(data_a_cleared["market_history"]) == 0
        assert len(data_a_cleared["scheme_history"]) == 0
        assert len(data_a_cleared["recent_activities"]) == 0

        # Verify Farmer B's history remains completely intact!
        hist_b_intact = client.get("/api/v1/history/all", headers=headers_b)
        data_b_intact = hist_b_intact.json()
        assert len(data_b_intact["weather_history"]) > 0
        assert len(data_b_intact["market_history"]) > 0

    def test_unauthenticated_history_access_denied(self, client):
        """Verify unauthenticated requests to history endpoints are rejected."""
        res_all = client.get("/api/v1/history/all")
        assert res_all.status_code == 401

        res_clear = client.delete("/api/v1/history/all")
        assert res_clear.status_code == 401
