"""Unit and integration tests for AI Agricultural Chatbot API endpoint and service supporting General Crop Assistant."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chatbot_service import chatbot_service

client = TestClient(app)


class TestChatbotService:
    """Unit tests for ChatbotService multi-crop extraction, intent detection, and context memory."""

    def test_multi_crop_extraction(self):
        assert chatbot_service._extract_crop("What fertilizer should I use for paddy?", []) == "Paddy"
        assert chatbot_service._extract_crop("Chilli ge yava fertilizer?", []) == "Chilli"
        assert chatbot_service._extract_crop("Groundnut cultivation advice", []) == "Groundnut"
        assert chatbot_service._extract_crop("Ragi cultivation hege madodu?", []) == "Ragi"
        assert chatbot_service._extract_crop("What is the price of tomato?", []) == "Tomato"
        assert chatbot_service._extract_crop("Corn ge yava fertilizer use madbeku?", []) == "Corn"

    def test_unknown_crop_asking(self):
        # When crop is unknown and question requires crop context
        res = chatbot_service._synthesize_fallback_response("What fertilizer should I use?", "fertilizer", None, "en", {}, None)
        assert "specify which crop" in res.lower()

        res_kn = chatbot_service._synthesize_fallback_response("ಯಾವ ಗೊಬ್ಬರ ಬಳಸಬೇಕು?", "fertilizer", None, "kn", {}, None)
        assert "ಯಾವ ಬೆಳೆಯನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ" in res_kn

    def test_conversation_crop_context_memory_and_switch(self):
        # 1. User says "I am growing paddy."
        crop1 = chatbot_service._extract_crop("I am growing paddy.", [])
        assert crop1 == "Paddy"

        history1 = [
            {"sender": "user", "text": "I am growing paddy."},
            {"sender": "bot", "text": "Understood! I can help you with paddy cultivation."}
        ]
        # 2. User asks "What fertilizer should I use?" -> remembers Paddy from history
        crop2 = chatbot_service._extract_crop("What fertilizer should I use?", history1)
        assert crop2 == "Paddy"

        history2 = history1 + [
            {"sender": "user", "text": "What fertilizer should I use?"},
            {"sender": "bot", "text": "Fertilizer management for Paddy..."}
        ]
        # 3. User asks "How much water does it need?" -> remembers Paddy from history
        crop3 = chatbot_service._extract_crop("How much water does it need?", history2)
        assert crop3 == "Paddy"

        # 4. User changes crop: "Actually I am growing corn now."
        crop4 = chatbot_service._extract_crop("Actually I am growing corn now.", history2)
        assert crop4 == "Corn"

        history3 = history2 + [
            {"sender": "user", "text": "Actually I am growing corn now."},
            {"sender": "bot", "text": "Updated crop context to Corn."}
        ]
        # 5. Next question refers to Corn
        crop5 = chatbot_service._extract_crop("What fertilizer should I use?", history3)
        assert crop5 == "Corn"

    def test_weather_isolation(self):
        # Weather data must NOT be forced into non-weather queries
        intent_scheme = chatbot_service._detect_intent("What government schemes are available?", [])
        assert intent_scheme == "government_scheme"

        intent_market = chatbot_service._detect_intent("What is the market price of paddy?", [])
        assert intent_market in ["market_price", "market_prediction"]


class TestChatbotEndpoints:
    """Integration test suite for POST /api/v1/chat."""

    def test_chat_unknown_crop_prompt(self):
        payload = {
            "message": "What fertilizer should I use?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "crop" in data["response"].lower() or "which" in data["response"].lower() or "specify" in data["response"].lower()

    def test_chat_paddy_fertilizer_query(self):
        payload = {
            "message": "Paddy ge yava fertilizer use madbeku?",
            "language": "kn",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] in ["fertilizer", "general_agriculture"]
        assert "Paddy" in data["response"] or "ಬೆಳೆಗೆ" in data["response"] or "ಗೊಬ್ಬರ" in data["response"]

    def test_chat_groundnut_cultivation_query(self):
        payload = {
            "message": "How can I cultivate groundnut?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Groundnut" in data["response"] or "groundnut" in data["response"].lower()

    def test_chat_ragi_kanglish_query(self):
        payload = {
            "message": "Ragi cultivation hege madodu?",
            "language": "kn",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Ragi" in data["response"] or "ರಾಗಿ" in data["response"] or "ಕೃಷಿ" in data["response"]

    def test_chat_chilli_fertilizer_query(self):
        payload = {
            "message": "Chilli ge yava fertilizer?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Chilli" in data["response"] or "fertilizer" in data["response"].lower()

    def test_chat_schemes_no_weather_leakage(self):
        payload = {
            "message": "What government schemes are available?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "government_scheme"
        assert "PM-KISAN" in data["response"] or "scheme" in data["response"].lower()
        assert "Humidity" not in data["response"] and "Temperature" not in data["response"]

    def test_chat_paddy_market_price_query(self):
        payload = {
            "message": "What is the market price of paddy?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "market_price"
        assert "Paddy" in data["response"] or "paddy" in data["response"].lower()
