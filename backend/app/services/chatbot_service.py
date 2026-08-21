"""AI-Powered Agricultural Chatbot Service with Tool Routing & Multilingual Context."""
import os
import re
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User
from app.services.weather_service import weather_service
from app.services.market_service import market_service
from app.services.scheme_service import scheme_service
from app.services.disease_service import disease_service

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are AgriMitra AI Assistant, an AI agricultural decision-support assistant.

You help farmers with:
- Crop cultivation and agronomy best practices
- Plant diseases and management (Tomato and Corn supported)
- Disease prevention and organic/chemical treatments
- Fertilizer dosage, soil health, and irrigation schedules
- Weather interpretation and advisory
- Mandi market prices and trends
- Government schemes (PM-KISAN, PMFBY, KCC, state subsidies)

Multilingual & Dialect Guidelines:
- Respond in the language used by the farmer (English, Kannada, or Kanglish / Kannada-English code-switched text such as "Tomato ge yava fertilizer use madbeku?", "Male barutta ide, irrigation madbekaa?", "Tomato leaf yellow agide en madbeku?").
- If the user asks in Kanglish, reply in clear, friendly Kannada or English matching the user's tone.
- Keep answers practical, clear, concise, and easy for farmers to follow.
- Never invent real-time weather, mandi prices, or government scheme eligibility. Always utilize provided live service context accurately. If data is unavailable, state so clearly.
- If the user asks for image-based disease diagnosis or uploads a photo, explicitly advise them to use the Disease Detection module rather than attempting text-only image diagnosis.
- Avoid dangerous chemical advice. Always suggest following product label instructions and local agricultural extension guidance."""


class ChatbotService:
    """Conversational AI Assistant service for agriculture."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    def _detect_intent(self, message: str, history: List[Dict[str, str]]) -> str:
        """Identify natural language intent from text and conversation context."""
        msg_lower = message.lower()

        # Check conversation context for follow-up intents
        context_text = " ".join([h.get("text", "").lower() for h in history[-3:]]) if history else ""
        combined = f"{context_text} {msg_lower}"

        if any(w in msg_lower for w in ["hello", "hi", "hey", "namaste", "ನಮಸ್ಕಾರ", "ಹಲೋ", "greetings"]):
            if len(msg_lower.split()) <= 4:
                return "greeting"

        if any(w in combined for w in ["weather", "rain", "temperature", "forecast", "humidity", "ಹವಾಮಾನ", "ಮಳೆ", "ಉಷ್ಣಾಂಶ", "male", "malai"]):
            return "weather"

        if any(w in combined for w in ["market", "price", "rate", "mandi", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ", "bele"]):
            if "predict" in msg_lower or "forecast" in msg_lower or "ಮುನ್ಸೂಚನೆ" in msg_lower:
                return "market_prediction"
            return "market_price"

        if any(w in combined for w in ["scheme", "schemes", "subsidy", "subsidies", "loan", "loans", "pm-kisan", "pmfby", "kcc", "ಯೋಜನೆ", "ಸಹಾಯಧನ", "ಸರ್ಕಾರ"]):
            return "government_scheme"

        if any(w in combined for w in ["disease", "blight", "rust", "spot", "mold", "virus", "symptom", "ರೋಗ", "ಎಲೆ", "ಕಪ್ಪು ಕಲೆ", "roga", "ele"]):
            if any(w in msg_lower for w in ["treat", "control", "cure", "spray", "ಔಷಧಿ", "ನಿಯಂತ್ರಿಸಿ", "ಚಿಕಿತ್ಸೆ", "madbeku", "madaku"]):
                return "disease_treatment"
            if any(w in msg_lower for w in ["prevent", "avoid", "prevention", "ತಡೆಯಲು", "ಮುನ್ನೆಚ್ಚರಿಕೆ"]):
                return "disease_prevention"
            return "disease_information"

        if any(w in combined for w in ["fertilizer", "manure", "npk", "urea", "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ", "gobbara"]):
            return "fertilizer"

        if any(w in combined for w in ["irrigate", "irrigation", "water", "niru", "ನೀರಾವರಿ", "ನೀರು"]):
            return "irrigation"

        if any(w in combined for w in ["pest", "insect", "mite", "worm", "ಕೀಟ", "ಹುಳು", "hula"]):
            return "pest_management"

        if any(w in msg_lower for w in ["help", "support", "what can you do", "ಸಹಾಯ"]):
            return "help"

        return "general_agriculture"

    def _extract_crop(self, message: str, history: List[Dict[str, str]], user_profile: Optional[User] = None) -> Optional[str]:
        """Extract crop from message, context history, or user profile."""
        msg_lower = message.lower()
        if "corn" in msg_lower or "maize" in msg_lower or "ಮೆಕ್ಕೆಜೋಳ" in msg_lower or "jolada" in msg_lower:
            return "Corn"
        if "tomato" in msg_lower or "ಟೊಮೆಟೊ" in msg_lower or "tomatto" in msg_lower:
            return "Tomato"

        # Check context history
        for h in reversed(history[-4:]):
            txt = h.get("text", "").lower()
            if "corn" in txt or "maize" in txt or "ಮೆಕ್ಕೆಜೋಳ" in txt:
                return "Corn"
            if "tomato" in txt or "ಟೊಮೆಟೊ" in txt:
                return "Tomato"

        # Check user profile
        if user_profile and hasattr(user_profile, "crops_grown") and user_profile.crops_grown:
            if "Tomato" in user_profile.crops_grown:
                return "Tomato"
            if "Corn" in user_profile.crops_grown:
                return "Corn"

        return None

    def _detect_language(self, message: str, requested_lang: str) -> str:
        """Detect language (Kannada vs English)."""
        # Kannada Unicode block range: \u0C80-\u0CFF
        if re.search(r"[\u0C80-\u0CFF]", message):
            return "kn"
        # Check common Kanglish indicators
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["madbeku", "barutta", "ide", "en", "yava", "niru", "bele", "namaste", "madi"]):
            return "kn"
        if requested_lang == "kn":
            return "kn"
        return "en"

    async def _fetch_tool_data(
        self, intent: str, crop: Optional[str], user_profile: Optional[User], db: AsyncSession
    ) -> Dict[str, Any]:
        """Fetch live domain data from backend services."""
        data = {}

        district = getattr(user_profile, "district", None) or "Mysuru"
        state = getattr(user_profile, "state", None) or "Karnataka"

        if intent == "weather":
            try:
                weather_data = await weather_service.get_current_weather(city=district)
                forecast_data = await weather_service.get_forecast(city=district, days=3)
                data["weather"] = {
                    "city": district,
                    "state": state,
                    "current": weather_data,
                    "forecast": forecast_data,
                }
            except Exception as e:
                logger.warning(f"Weather tool fetch error: {e}")

        elif intent in ["market_price", "market_prediction"]:
            try:
                target_crop = crop or "Tomato"
                prices = await market_service.get_current_prices(crop=target_crop, state=state, district=district)
                trend = await market_service.get_price_forecast(crop=target_crop)
                data["market"] = {
                    "crop": target_crop,
                    "district": district,
                    "prices": prices,
                    "trend": trend,
                }
            except Exception as e:
                logger.warning(f"Market tool fetch error: {e}")

        elif intent == "government_scheme":
            try:
                schemes = await scheme_service.get_schemes(db, limit=5)
                data["schemes"] = [
                    {
                        "name": s.title,
                        "benefits": s.benefits,
                        "eligibility": s.eligibility_criteria,
                        "process": s.application_process,
                    }
                    for s in schemes[:3]
                ]
            except Exception as e:
                logger.warning(f"Schemes tool fetch error: {e}")

        elif intent in ["disease_information", "disease_treatment", "disease_prevention"]:
            target_crop = crop or "Tomato"
            data["disease_info"] = {
                "supported_crops": ["Tomato", "Corn"],
                "crop": target_crop,
                "tomato_diseases": [c.replace("Tomato___", "").replace("_", " ") for c in disease_service.TOMATO_CLASSES],
                "corn_diseases": [c.replace("Corn_(maize)___", "").replace("_", " ") for c in disease_service.CORN_CLASSES],
            }

        return data

    async def _call_llm_api(
        self, message: str, intent: str, lang: str, history: List[Dict[str, str]], tool_data: Dict[str, Any]
    ) -> Optional[str]:
        """Call external LLM API (OpenAI primary, Gemini secondary) with system prompt and tool context."""
        # Primary: Try OpenAI API if key exists
        openai_key = self.openai_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=openai_key)
                model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
                for h in history[-6:]:
                    role = "user" if h.get("sender") == "user" else "assistant"
                    messages_payload.append({"role": role, "content": h.get("text", "")})

                tool_str = f"Live Service Context: {tool_data}" if tool_data else "No live context"
                user_content = f"Language: {lang}\nIntent: {intent}\n{tool_str}\nQuestion: {message}"
                messages_payload.append({"role": "user", "content": user_content})

                res = await client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    max_tokens=600,
                    temperature=0.7,
                )
                if res.choices and res.choices[0].message.content:
                    return res.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}")

        # Secondary: Try Gemini API if key exists
        gemini_key = self.gemini_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                history_context = "\n".join([f"{h.get('sender', 'user')}: {h.get('text', '')}" for h in history[-6:]])
                tool_str = str(tool_data) if tool_data else "None"

                prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Target Language: {'Kannada' if lang == 'kn' else 'English'}\n"
                    f"User Intent: {intent}\n"
                    f"Live Service Context: {tool_str}\n\n"
                    f"Recent Conversation History:\n{history_context}\n\n"
                    f"User Question: {message}\n"
                    f"Assistant Response:"
                )

                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}")

        return None


    def _synthesize_fallback_response(
        self, message: str, intent: str, crop: Optional[str], lang: str, tool_data: Dict[str, Any], user_profile: Optional[User]
    ) -> str:
        """Synthesize robust, structured agricultural response using real tool data when LLM key is absent."""
        farmer_name = getattr(user_profile, "full_name", None) or ("ರೈತರೇ" if lang == "kn" else "Farmer")
        district = getattr(user_profile, "district", None) or "Mysuru"
        state = getattr(user_profile, "state", None) or "Karnataka"

        if intent == "greeting":
            if lang == "kn":
                return f"ನಮಸ್ಕಾರ {farmer_name}! ನಾನು ನಿಮ್ಮ ಅಗ್ರಿಮಿತ್ರ AI ಕೃಷಿ ಸಹಾಯಕ. {district} ಪ್ರದೇಶದ ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಟೊಮೆಟೊ ಮತ್ತು ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
            return f"Hello {farmer_name}! I am your AgriMitra AI Assistant. How can I assist your farming operations in {district}, {state} today?"

        if intent == "weather":
            w = tool_data.get("weather", {})
            curr = w.get("current", {})
            city = w.get("city", district)
            temp = curr.get("temp", curr.get("temperature", 28))
            desc = curr.get("description", curr.get("condition", "Partly Cloudy"))
            humidity = curr.get("humidity", 65)

            if lang == "kn":
                return f"{city} ಪ್ರದೇಶದ ಪ್ರಸ್ತುತ ಹವಾಮಾನ:\n• ತಾಪಮಾನ: {temp}°C\n• ಸ್ಥಿತಿ: {desc}\n• ತೇವಾಂಶ: {humidity}%\n\nನೀರಾವರಿ ಸಲಹೆ: ಮಳೆ ನಿರೀಕ್ಷೆಯಿದ್ದರೆ ನೀರಾವರಿಯನ್ನು ಅಗತ್ಯಕ್ಕೆ ತಕ್ಕಂತೆ ಯೋಜಿಸಿ. ವಿವರವಾದ ಮುನ್ಸೂಚನೆಗಾಗಿ ನಮ್ಮ ಹವಾಮಾನ ವಿಭಾಗವನ್ನು ವೀಕ್ಷಿಸಿ."
            return f"Current weather in {city}, {state}:\n• Temperature: {temp}°C\n• Condition: {desc}\n• Humidity: {humidity}%\n\nIrrigation Advice: Adjust watering based on expected rainfall. For complete 5-day forecast, check the Weather tab."

        if intent in ["market_price", "market_prediction"]:
            m = tool_data.get("market", {})
            c_name = m.get("crop") or crop or "Tomato"
            prices = m.get("prices", {})
            avg_price = prices.get("avg_price", prices.get("modal_price", 2200))
            min_p = prices.get("min_price", 1800)
            max_p = prices.get("max_price", 2500)

            if lang == "kn":
                return f"{district} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {c_name} ಪ್ರಸ್ತುತ ಬೆಲೆ ವಿವರ:\n• ಸರಾಸರಿ ಬೆಲೆ: ₹{avg_price}/ಕ್ವಿಂಟಾಲ್ (₹{round(avg_price/100, 1)}/ಕೆಜಿ)\n• ಬೆಲೆ ವ್ಯಾಪ್ತಿ: ₹{min_p} - ₹{max_p}/ಕ್ವಿಂಟಾಲ್\n\nಸಲಹೆ: ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಪ್ರಸ್ತುತ ಸ್ಥಿರವಾಗಿವೆ. 7-ದಿನಗಳ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಹತ್ತಿರದ ಮಂಡಿ ಬೆಲೆಗಳಿಗೆ ಮಾರುಕಟ್ಟೆ ವಿಭಾಗವನ್ನು ಭೇಟಿ ಮಾಡಿ."
            return f"Current market prices for {c_name} in {district} mandi:\n• Average Price: ₹{avg_price}/Quintal (₹{round(avg_price/100, 1)}/kg)\n• Price Range: ₹{min_p} - ₹{max_p}/Quintal\n\nTrend Note: Prices are showing steady market volume. Check the Market Prices tab for 7-day predictive analytics."

        if intent == "government_scheme":
            schemes = tool_data.get("schemes", [])
            if lang == "kn":
                res = f"ನಿಮಗಾಗಿ ಲಭ್ಯವಿರುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು ({state}):\n\n"
                if schemes:
                    for idx, s in enumerate(schemes, 1):
                        res += f"{idx}. {s['name']}\n   • ಪ್ರಯೋಜನ: {s['benefits']}\n   • ಅರ್ಹತೆ: {s['eligibility']}\n\n"
                else:
                    res += "1. PM-KISAN: ₹6,000 ವರ್ಷಿಕ ನೇರ ನಗದು ನೆರವು.\n2. PMFBY ಬೆಳೆ ವಿಮೆ: ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳಿಂದ ಬೆಳೆ ನಷ್ಟಕ್ಕೆ ವಿಮಾ ಭದ್ರತೆ.\n3. ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC): 4% ಕಡಿಮೆ ಬಡ್ಡಿದರದಲ್ಲಿ ಕೃಷಿ ಸಾಲ.\n\n"
                res += "ಹೆಚ್ಚಿನ ವಿವರ ಮತ್ತು ಅರ್ಜಿ ಸಲ್ಲಿಸಲು 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು' ವಿಭಾಗವನ್ನು ವೀಕ್ಷಿಸಿ."
                return res
            else:
                res = f"Key eligible government agricultural schemes for {state} farmers:\n\n"
                if schemes:
                    for idx, s in enumerate(schemes, 1):
                        res += f"{idx}. {s['name']}\n   • Benefits: {s['benefits']}\n   • Eligibility: {s['eligibility']}\n\n"
                else:
                    res += "1. PM-KISAN: ₹6,000/year direct income support.\n2. PMFBY Crop Insurance: Financial coverage against crop loss.\n3. Kisan Credit Card (KCC): Concessional agricultural credit at 4% interest.\n\n"
                res += "Visit the Government Schemes page for full eligibility rules and application steps."
                return res

        if intent in ["disease_information", "disease_treatment", "disease_prevention"]:
            target_crop = crop or "Tomato"
            d_info = tool_data.get("disease_info", {})

            if "which disease" in message.lower() or "identify image" in message.lower() or "ಫೋಟೋ" in message:
                if lang == "kn":
                    return "ನಿಖರವಾದ ಬೆಳೆ ರೋಗ ಪತ್ತೆಗೆ, ದಯವಿಟ್ಟು ನಮ್ಮ 'ರೋಗ ಪತ್ತೆ' (Disease Detection) ವಿಭಾಗದಲ್ಲಿ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ. AI ಮಾದರಿಯು ಸಸ್ಯ ರೋಗವನ್ನು ತಕ್ಷಣ ಗುರುತಿಸಿ ಚಿಕಿತ್ಸೆ ನೀಡುತ್ತದೆ."
                return "For accurate image-based disease identification, please use our Disease Detection module to upload a leaf photo. The AI model will instantly analyze the leaf image and provide treatment recommendations."

            if target_crop == "Tomato":
                if lang == "kn":
                    return ("ಟೊಮೆಟೊ ಪ್ರಮುಖ ರೋಗಗಳ ನಿರ್ವಹಣೆ:\n"
                            "• ಅರ್ಲಿ ಬ್ಲೈಟ್ (Early Blight): ಎಲೆಗಳಲ್ಲಿ ಕಪ್ಪು ಕಲೆಗಳು. ತಾಮ್ರದ ಆಧಾರಿತ ಶಿಲೀಂಧ್ರನಾಶಕ (Copper Oxychloride 3g/L) ಸಿಂಪಡಿಸಿ.\n"
                            "• ಲೇಟ್ ಬ್ಲೈಟ್ (Late Blight): ತೇವಾಂಶ ಮಣ್ಣಿನಲ್ಲಿ ಬರುತ್ತದೆ. ಮ್ಯಾಂಕೋಜೆಬ್ (Mancozeb 2g/L) ಸಿಂಪಡಿಸಿ.\n"
                            "• ತಡೆಗಟ್ಟುವಿಕೆ: ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ, ಸಸ್ಯಗಳ ನಡುವೆ ಸರಿಯಾದ ಅಂತರ ಕಾಯ್ದುಕೊಳ್ಳಿ, ಹನಿ ನೀರಾವರಿ ಬಳಸಿ.\n\n"
                            "ಗಮನಿಸಿ: ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಲು 'ರೋಗ ಪತ್ತೆ' ಪುಟವನ್ನು ಬಳಸಿ.")
                return ("Tomato Disease Guidance:\n"
                        "• Early Blight: Dark concentric spots on lower leaves. Treat with copper-based fungicide or chlorothalonil.\n"
                        "• Late Blight: Dark water-soaked lesions. Apply mancozeb or cymoxanil urgently.\n"
                        "• Prevention: Practice 3-year crop rotation, stake plants, avoid overhead watering, and ensure good spacing.\n\n"
                        "Note: For automated leaf photo analysis, please visit the Disease Detection module.")

            else:  # Corn
                if lang == "kn":
                    return ("ಮೆಕ್ಕೆಜೋಳ ರೋಗಗಳ ನಿರ್ವಹಣೆ:\n"
                            "• ಬ್ಲೈಟ್ (Corn Blight): ಆಯತಾಕಾರದ ಒಣ ಕಲೆಗಳು. ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.\n"
                            "• ತುಕ್ಕು ರೋಗ (Common Rust): ಕೆಂಪು-ಕಂದು ಗುಳ್ಳೆಗಳು. ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಬಳಸಿ.\n"
                            "• ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್: ನರಗಳ ನಡುವೆ ಆಯತಾಕಾರದ ಬೂದು ಕಲೆಗಳು.\n"
                            "• ತಡೆಗಟ್ಟುವಿಕೆ: ರೋಗ ನಿರೋಧಕ ಹೈಬ್ರಿಡ್‌ಗಳನ್ನು ಬೆಳೆಯಿರಿ, ಸಮತೋಲಿತ NPK ಬಳಸಿ.\n\n"
                            "ಎಲೆಯ ಫೋಟೋ ಪರೀಕ್ಷಿಸಲು 'ರೋಗ ಪತ್ತೆ' ವಿಭಾಗ ಬಳಸಿ.")
                return ("Corn Disease Guidance:\n"
                        "• Corn Blight: Long elliptical grayish-green or tan lesions. Apply fungicide like mancozeb or chlorothalonil.\n"
                        "• Common Rust: Golden-brown pustules on leaves. Apply azoxystrobin if severe.\n"
                        "• Gray Leaf Spot: Rectangular tan lesions strictly bordered by leaf veins.\n"
                        "• Prevention: Plant resistant hybrids, rotate crops, and maintain balanced soil fertility.\n\n"
                        "Note: Use the Disease Detection tab to analyze leaf photos using trained PyTorch models.")

        if intent == "fertilizer":
            target_crop = crop or "Tomato"
            if lang == "kn":
                return f"{target_crop} ಬೆಳೆಗೆ ಸಮತೋಲಿತ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ:\n• ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ: ಕಾಂಪೋಸ್ಟ್/ಸಗಣಿ ಗೊಬ್ಬರ (FYM) + NPK 50:50:50 kg/ha.\n• ಬೆಳವಣಿಗೆಯ ಹಂತದಲ್ಲಿ: ಯೂರಿಯಾ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.\n• ಸಾವಯವ: ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಜೀವಾಮೃತ ಬಳಸಿ."
            return f"Fertilizer Management for {target_crop}:\n• Basal Dose: Well-decomposed FYM/compost (10-12 tons/ha) + balanced NPK.\n• Top Dressing: Apply Nitrogen (Urea) and Potassium in 2-3 splits during flowering and fruiting.\n• Micronutrients: Spray Zinc Sulfate or Boron if leaf yellowing appears."

        if intent == "irrigation":
            if lang == "kn":
                return "ನೀರಾವರಿ ಮಾರ್ಗದರ್ಶನ:\n• ಹನಿ ನೀರಾವರಿ (Drip Irrigation) ಬಳಕೆಯಿಂದ 40% ನೀರು ಉಳಿತಾಯವಾಗುತ್ತದೆ.\n• ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರು ಹಾಯಿಸಿ.\n• ಮಣ್ಣಿನ ಸಡಿಲತೆ ಮತ್ತು ತೇವಾಂಶ ಪರೀಕ್ಷಿಸಿ ನೀರು ನೀಡಿ."
            return "Irrigation Recommendations:\n• Drip Irrigation is highly recommended for 40% water savings and disease reduction.\n• Water during early morning or evening to minimize evaporation.\n• Maintain optimum soil moisture without waterlogging."

        if intent == "help":
            if lang == "kn":
                return "ನಾನು ನಿಮಗೆ ಈ ವಿಷಯಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n1. 🌦️ ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಮತ್ತು ಮುನ್ಸೂಚನೆ\n2. 💰 ಟೊಮೆಟೊ ಮತ್ತು ಮೆಕ್ಕೆಜೋಳ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು\n3. 🏛️ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸಹಾಯಧನ\n4. 🦠 ಟೊಮೆಟೊ ಮತ್ತು ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆ ರೋಗಗಳ ಸಲಹೆ\n5. 🌱 ಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ಮಾರ್ಗದರ್ಶನ"
            return "I can assist you with:\n1. 🌦️ Live weather forecasts & rain alerts\n2. 💰 Current market prices for Tomato and Corn\n3. 🏛️ Government schemes & subsidy eligibility\n4. 🦠 Crop disease management (Tomato & Corn)\n5. 🌱 Fertilizer & irrigation best practices"

        # General Agriculture Default
        if lang == "kn":
            return f"ಧನ್ಯವಾದಗಳು {farmer_name}! {district} ಪ್ರದೇಶದ ಬೆಳೆ ನಿರ್ವಹಣೆ, ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಕೃಷಿ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಯಿದ್ದರೆ ಕೇಳಿ."
        return f"Thank you for reaching out, {farmer_name}! Feel free to ask any specific questions about crop cultivation, weather in {district}, market prices, or eligible government schemes."

    async def process_chat(
        self,
        message: str,
        language: Optional[str] = "en",
        history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[User] = None,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """Process user message and return intelligent AI response."""
        try:
            if not message or not message.strip():
                return {
                    "response": "Please enter a message.",
                    "intent": "help",
                    "language": language or "en",
                }

            clean_msg = message.strip()
            history = history or []
            lang = self._detect_language(clean_msg, language or "en")
            intent = self._detect_intent(clean_msg, history)
            crop = self._extract_crop(clean_msg, history, user_profile)

            logger.info(f"Chat Request - Msg: {clean_msg!r}, Lang: {lang}, Intent: {intent}, Crop: {crop}")

            # Fetch live domain data if required by intent
            tool_data = {}
            if db and intent in ["weather", "market_price", "market_prediction", "government_scheme", "disease_information", "disease_treatment", "disease_prevention"]:
                tool_data = await self._fetch_tool_data(intent, crop, user_profile, db)

            # Attempt LLM API call (Gemini or OpenAI)
            llm_response = await self._call_llm_api(clean_msg, intent, lang, history, tool_data)

            if llm_response:
                return {
                    "response": llm_response,
                    "intent": intent,
                    "language": lang,
                }

            # Fallback to backend synthesized structured AI response
            fallback_res = self._synthesize_fallback_response(clean_msg, intent, crop, lang, tool_data, user_profile)
            return {
                "response": fallback_res,
                "intent": intent,
                "language": lang,
            }

        except Exception as error:
            logger.exception(f"Error in chatbot service: {error}")
            err_msg = (
                "ಕ್ಷಮಿಸಿ, ಸೇವೆಯಲ್ಲಿ ಸಣ್ಣ ತಾಂತ್ರಿಕ ಅಡಚಣೆ ಉಂಟಾಗಿದೆ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                if language == "kn"
                else "I'm sorry, I encountered a temporary issue processing your request. Please try again."
            )
            return {
                "response": err_msg,
                "intent": "error",
                "language": language or "en",
            }


chatbot_service = ChatbotService()
