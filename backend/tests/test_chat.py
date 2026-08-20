"""Unit and integration tests for AI Agricultural Chatbot API endpoint and service."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chatbot_service import chatbot_service

client = TestClient(app)


class TestChatbotService:
    """Unit tests for ChatbotService intent detection and response generation."""

    def test_intent_detection_english(self):
        intent_weather = chatbot_service._detect_intent("Will it rain today?", [])
        assert intent_weather == "weather"

        intent_market = chatbot_service._detect_intent("What is the tomato price?", [])
        assert intent_market == "market_price"

        intent_scheme = chatbot_service._detect_intent("Are there government subsidies for small farmers?", [])
        assert intent_scheme == "government_scheme"

        intent_disease = chatbot_service._detect_intent("How do I control tomato early blight?", [])
        assert intent_disease == "disease_treatment"

    def test_intent_detection_kannada(self):
        intent_weather_kn = chatbot_service._detect_intent("ಇವತ್ತು ಹವಾಮಾನ ಹೇಗಿದೆ?", [])
        assert intent_weather_kn == "weather"

        intent_market_kn = chatbot_service._detect_intent("ಟೊಮೆಟೊ ಬೆಲೆ ಎಷ್ಟು?", [])
        assert intent_market_kn == "market_price"

        intent_scheme_kn = chatbot_service._detect_intent("ರೈತರಿಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳಿವೆ?", [])
        assert intent_scheme_kn == "government_scheme"

    def test_intent_detection_mixed_language(self):
        intent_fertilizer = chatbot_service._detect_intent("Tomato ge yava fertilizer use madbeku?", [])
        assert intent_fertilizer == "fertilizer"

        intent_market_mixed = chatbot_service._detect_intent("Tomato ಬೆಲೆ ಎಷ್ಟು?", [])
        assert intent_market_mixed == "market_price"

    def test_context_memory_coreference(self):
        history = [
            {"sender": "user", "text": "What is tomato early blight?"},
            {"sender": "bot", "text": "Early blight is a fungal disease causing dark spots."}
        ]
        intent = chatbot_service._detect_intent("How do I treat it?", history)
        crop = chatbot_service._extract_crop("How do I treat it?", history)

        assert intent == "disease_treatment"
        assert crop == "Tomato"

    def test_disease_routing_crop_limits(self):
        # Disease knowledge supports Tomato and Corn only, not Paddy
        disease_info = chatbot_service._extract_crop("Tell me about paddy blast disease", [])
        assert disease_info is None or disease_info not in ["Paddy"]


class TestChatbotEndpoints:
    """Integration test suite for POST /api/v1/chat."""

    def test_chat_success_english(self):
        payload = {
            "message": "What fertilizer is good for tomato?",
            "language": "en",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["intent"] in ["fertilizer", "disease_information", "general_agriculture"]
        assert len(data["response"]) > 10

    def test_chat_success_kannada(self):
        payload = {
            "message": "ಇವತ್ತು ಹವಾಮಾನ ಹೇಗಿದೆ?",
            "language": "kn",
            "conversation_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "kn"
        assert data["intent"] == "weather"
        assert "ತಾಪಮಾನ" in data["response"] or "ಹವಾಮಾನ" in data["response"]

    def test_chat_weather_routing(self):
        payload = {
            "message": "Will it rain today in Mysuru?",
            "language": "en"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "weather"
        assert "Temperature" in data["response"] or "Humidity" in data["response"] or "weather" in data["response"].lower()

    def test_chat_market_routing(self):
        payload = {
            "message": "What is today's tomato market price?",
            "language": "en"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "market_price"
        assert "Price" in data["response"] or "Quintal" in data["response"] or "Tomato" in data["response"]

    def test_chat_schemes_routing(self):
        payload = {
            "message": "What government schemes are available for farmers?",
            "language": "en"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "government_scheme"
        assert "PM-KISAN" in data["response"] or "scheme" in data["response"].lower()

    def test_chat_disease_routing(self):
        payload = {
            "message": "What disease affects tomato leaves with dark spots?",
            "language": "en"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] in ["disease_information", "disease_treatment"]
        assert "Tomato" in data["response"] or "Blight" in data["response"]

    def test_chat_empty_message_validation(self):
        payload = {
            "message": "   ",
            "language": "en"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 400
        assert "Message cannot be empty" in response.json()["detail"]

    def test_chat_context_memory_endpoint(self):
        payload = {
            "message": "How do I treat it?",
            "language": "en",
            "conversation_history": [
                {"sender": "user", "text": "What is tomato early blight?"},
                {"sender": "bot", "text": "Early blight is caused by Alternaria solani fungus."}
            ]
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "disease_treatment"
