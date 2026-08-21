"""AI-Powered Agricultural Chatbot Service supporting general crop guidance, tool routing & conversation context memory."""
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

SYSTEM_PROMPT = """You are AgriMitra AI Assistant, an intelligent GENERAL agricultural decision-support assistant for farmers.

Core Principles:
1. GENERAL AGRICULTURAL ASSISTANT (ALL CROPS):
   - You provide expert farming guidance for ALL crops including Tomato, Corn/Maize, Paddy/Rice, Potato, Chilli, Onion, Beans, Groundnut, Cotton, Sugarcane, Ragi, Wheat, Pulses, Vegetables, Fruits, and any crop mentioned by the farmer.
   - Do NOT default to Tomato or Corn when another crop or no crop is mentioned.

2. CROP CONTEXT MEMORY:
   - Identify the crop mentioned in the question or in recent conversation history.
   - If a farmer previously stated they are growing a specific crop (e.g. "I am growing paddy"), keep answering questions (fertilizer, irrigation, disease, spacing) for PADDY until the farmer changes crop (e.g. "Now I am growing corn").
   - If the user asks a crop-specific question (e.g. "What fertilizer should I use?") and NO crop is mentioned in the prompt or conversation history, politely ask: "Which crop are you growing?" in the user's language.

3. INTENT & TOOL DATA ROUTING:
   - Weather Rule: ONLY discuss weather/forecast when the user asks about weather/rain/temperature/climate or explicitly requests weather-based farming advice. Do NOT inject weather info into fertilizer, market price, or scheme questions.
   - Market Rule: Use real mandi price data when provided in Live Service Context. If price data for a specific crop (e.g. Paddy) is unavailable in the database, clearly state that price data is unavailable for that crop. Do NOT invent prices or substitute weather data.
   - Schemes Rule: Provide government scheme eligibility and benefits (PM-KISAN, PMFBY, KCC, subsidies).
   - Disease Rule: You can give general text disease guidance for any crop. However, if the user asks for image-based disease diagnosis, inform them that automated ML leaf image detection currently supports Tomato and Corn.

4. MULTILINGUAL & KANGLISH SUPPORT:
   - Respond naturally in the user's language: English, Kannada, or Kanglish (code-switched Kannada-English such as "Paddy ge estu neeru hakbeku?", "Tomato ge yava fertilizer use madbeku?", "Corn cultivation hege madodu?", "Groundnut ge yava fertilizer?", "Ragi cultivation hege madodu?").
   - Keep answers practical, clear, structured, and farmer-friendly.
"""

CROP_ALIASES = {
    "Tomato": ["tomato", "tomatto", "tomatode", "tomatoes", "ಟೊಮೆಟೊ", "ಟೊಮೇಟೊ"],
    "Corn": ["corn", "maize", "ಮೆಕ್ಕೆಜೋಳ", "jolada", "jola", "ಜೋಳ"],
    "Paddy": ["paddy", "rice", "ಬತ್ತ", "ಭತ್ತ", "bhatta", "batha", "anna"],
    "Potato": ["potato", "potatoes", "ಆಲೂಗಡ್ಡೆ", "alugadde", "alugadday"],
    "Chilli": ["chilli", "chili", "chillies", "ಮೆಣಸಿನಕಾಯಿ", "menasinakayi", "menasina"],
    "Onion": ["onion", "onions", "ಈರುಳ್ಳಿ", "irulli", "eerulli"],
    "Beans": ["beans", "bean", "ಹುರುಳಿಕಾಯಿ", "hurulikayi"],
    "Groundnut": ["groundnut", "peanut", "peanuts", "ಕಡಲೆಕಾಯಿ", "kadalekayi", "shenga"],
    "Cotton": ["cotton", "ಹತ್ತಿ", "hatti"],
    "Sugarcane": ["sugarcane", "ಕಬ್ಬು", "kabbu"],
    "Ragi": ["ragi", "finger millet", "ರಾಗಿ"],
    "Wheat": ["wheat", "ಗೋಧಿ", "godhi"],
    "Pulses": ["pulse", "pulses", "dal", "dhal", "ಬೇಳೆ", "bele"],
    "Vegetables": ["vegetable", "vegetables", "ತರಕಾರಿ", "tarakari"],
    "Fruits": ["fruit", "fruits", "ಹಣ್ಣು", "hannu"],
}


class ChatbotService:
    """Conversational AI Assistant service for general agriculture."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    def _extract_crop_from_text(self, text: str) -> Optional[str]:
        """Check a single text string for any known crop alias."""
        text_lower = text.lower()
        for normalized_crop, aliases in CROP_ALIASES.items():
            for alias in aliases:
                pattern = r"\b" + re.escape(alias) + r"\b"
                if re.search(pattern, text_lower):
                    return normalized_crop

        # Regex fallback for arbitrary crop mentions: "growing <crop>", "<crop> cultivation", "<crop> ge"
        match = re.search(r"\b(?:growing|cultivating|crop is|for)\s+([a-zA-Z]{3,15})\b", text_lower)
        if match:
            extracted = match.group(1).capitalize()
            if extracted not in ["Today", "Tomorrow", "Fertilizer", "Weather", "Water", "Disease"]:
                return extracted

        match_kn = re.search(r"\b([a-zA-Z]{3,15})\s+ge\b", text_lower)
        if match_kn:
            extracted = match_kn.group(1).capitalize()
            if extracted not in ["Today", "Tomorrow", "Me", "You", "Help"]:
                return extracted

        return None

    def _extract_crop(
        self,
        message: str,
        history: List[Dict[str, str]],
        user_profile: Optional[User] = None,
    ) -> Optional[str]:
        """Extract crop from message, context history, or user profile without forcing a default."""
        # 1. Check current message first
        crop = self._extract_crop_from_text(message)
        if crop:
            return crop

        # 2. Check conversation context history (most recent user message first)
        for h in reversed(history):
            txt = h.get("text", "")
            crop_in_hist = self._extract_crop_from_text(txt)
            if crop_in_hist:
                return crop_in_hist

        # 3. No crop found in prompt or history
        return None

    def _detect_intent(self, message: str, history: List[Dict[str, str]]) -> str:
        """Identify natural language intent from text."""
        msg_lower = message.lower()

        # Greetings (using word boundaries to prevent 'hi' inside 'chilli')
        if re.search(r"\b(hello|hi|hey|namaste|ನಮಸ್ಕಾರ|ಹಲೋ|greetings)\b", msg_lower):
            if len(msg_lower.split()) <= 4:
                return "greeting"

        # Crop declaration (e.g., "I am growing paddy", "Tomato", "Now I am growing corn")
        if any(w in msg_lower for w in ["growing", "cultivating", "my crop is", "ನಾನು", "ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ"]):
            extracted = self._extract_crop_from_text(msg_lower)
            if extracted:
                return "crop_declaration"

        # Weather intent (ONLY match explicit weather words in current message with word boundaries)
        if re.search(r"\b(weather|rain|temperature|forecast|humidity|climate|monsoon|ಹವಾಮಾನ|ಮಳೆ|ಉಷ್ಣಾಂಶ|male|malai)\b", msg_lower) or "rain fall" in msg_lower:
            return "weather"

        # Market prices / prediction
        if any(w in msg_lower for w in ["market", "price", "rate", "mandi", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ", "bele", "cost"]):
            if "predict" in msg_lower or "forecast" in msg_lower or "ಮುನ್ಸೂಚನೆ" in msg_lower:
                return "market_prediction"
            return "market_price"

        # Government schemes
        if any(w in msg_lower for w in ["scheme", "schemes", "subsidy", "subsidies", "loan", "loans", "pm-kisan", "pmfby", "kcc", "ಯೋಜನೆ", "ಸಹಾಯಧನ", "ಸರ್ಕಾರ"]):
            return "government_scheme"

        # Diseases & plant health
        if any(
            w in msg_lower
            for w in [
                "disease", "blight", "rust", "spot", "mold", "virus", "symptom", "rot",
                "infection", "wilt", "yellowing", "black spot", "ರೋಗ", "ಎಲೆ", "ಕಪ್ಪು ಕಲೆ", "roga", "ele"
            ]
        ):
            if any(w in msg_lower for w in ["treat", "control", "cure", "spray", "ಔಷಧಿ", "ನಿಯಂತ್ರಿಸಿ", "ಚಿಕಿತ್ಸೆ", "madbeku", "madaku"]):
                return "disease_treatment"
            if any(w in msg_lower for w in ["prevent", "avoid", "prevention", "ತಡೆಯಲು", "ಮುನ್ನೆಚ್ಚರಿಕೆ"]):
                return "disease_prevention"
            return "disease_information"

        # Fertilizer
        if any(w in msg_lower for w in ["fertilizer", "manure", "npk", "urea", "compost", "nitrogen", "potash", "phosphate", "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ", "gobbara"]):
            return "fertilizer"

        # Irrigation
        if any(w in msg_lower for w in ["irrigate", "irrigation", "water", "watering", "drip", "sprinkler", "niru", "neeru", "ನೀರಾವರಿ", "ನೀರು"]):
            return "irrigation"

        # Pest management
        if any(w in msg_lower for w in ["pest", "insect", "mite", "worm", "aphid", "caterpillar", "borer", "ಕೀಟ", "ಹುಳು", "hula"]):
            return "pest_management"

        # General cultivation practices
        if any(w in msg_lower for w in ["cultivate", "cultivation", "grow", "planting", "sowing", "spacing", "harvest", "hege madodu", "ಬೆಳೆಯುವುದು"]):
            return "cultivation_general"

        # Follow-up coreference check from context history (e.g., "How to treat it?", "How much water does it need?")
        if history and any(w in msg_lower for w in ["it", "this", "that", "them", "treat it", "water it"]):
            last_user_msg = next((h.get("text", "") for h in reversed(history) if h.get("sender") == "user"), "")
            if last_user_msg:
                return self._detect_intent(last_user_msg, [])

        if any(w in msg_lower for w in ["help", "support", "what can you do", "ಸಹಾಯ"]):
            return "help"

        return "general_agriculture"

    def _detect_language(self, message: str, requested_lang: str) -> str:
        """Detect language (Kannada vs English)."""
        if re.search(r"[\u0C80-\u0CFF]", message):
            return "kn"
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["madbeku", "barutta", "ide", "en", "yava", "niru", "bele", "namaste", "madi", "hege", "madodu", "hakbeku", "esthu"]):
            return "kn"
        if requested_lang == "kn":
            return "kn"
        return "en"

    async def _fetch_tool_data(
        self, intent: str, crop: Optional[str], user_profile: Optional[User], db: AsyncSession
    ) -> Dict[str, Any]:
        """Fetch live domain data ONLY for relevant intents (no weather leakage)."""
        data = {}
        district = getattr(user_profile, "district", None) or "Mysuru"
        state = getattr(user_profile, "state", None) or "Karnataka"

        # Weather tool: ONLY fetch when intent is weather!
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
            if crop:
                try:
                    prices = await market_service.get_current_prices(crop=crop, state=state, district=district)
                    trend = await market_service.get_price_forecast(crop=crop)
                    data["market"] = {
                        "crop": crop,
                        "district": district,
                        "prices": prices,
                        "trend": trend,
                    }
                except Exception as e:
                    logger.warning(f"Market tool fetch error for {crop}: {e}")
            else:
                data["market"] = {"crop": None, "note": "No crop specified for price query"}

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
            data["disease_info"] = {
                "ml_image_supported_crops": ["Tomato", "Corn"],
                "requested_crop": crop or "General",
                "note": "Automated leaf photo analysis in Disease Detection module supports Tomato and Corn. Text guidance available for all crops.",
            }

        return data

    async def _call_llm_api(
        self, message: str, intent: str, crop: Optional[str], lang: str, history: List[Dict[str, str]], tool_data: Dict[str, Any]
    ) -> Optional[str]:
        """Call external LLM API (OpenAI primary, Gemini secondary) with system prompt and tool context."""
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

                tool_str = f"Live Service Context: {tool_data}" if tool_data else "No live tool context"
                crop_str = f"Current Crop in Context: {crop}" if crop else "Current Crop in Context: UNKNOWN (Ask farmer if question requires a crop)"
                user_content = f"Language: {lang}\nIntent: {intent}\n{crop_str}\n{tool_str}\nFarmer Question: {message}"
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

        # Secondary: Gemini API if key exists
        gemini_key = self.gemini_key or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                history_context = "\n".join([f"{h.get('sender', 'user')}: {h.get('text', '')}" for h in history[-6:]])
                tool_str = str(tool_data) if tool_data else "None"
                crop_str = crop or "UNKNOWN"

                prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Target Language: {'Kannada' if lang == 'kn' else 'English'}\n"
                    f"User Intent: {intent}\n"
                    f"Current Crop: {crop_str}\n"
                    f"Live Service Context: {tool_str}\n\n"
                    f"Recent Conversation History:\n{history_context}\n\n"
                    f"Farmer Question: {message}\n"
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
        """Synthesize structured agricultural response for ANY crop when LLM key is absent."""
        farmer_name = getattr(user_profile, "full_name", None) or ("ರೈತರೇ" if lang == "kn" else "Farmer")
        district = getattr(user_profile, "district", None) or "Mysuru"
        state = getattr(user_profile, "state", None) or "Karnataka"

        if intent == "greeting":
            if lang == "kn":
                return f"ನಮಸ್ಕಾರ {farmer_name}! ನಾನು ನಿಮ್ಮ ಅಗ್ರಿಮಿತ್ರ AI ಕೃಷಿ ಸಹಾಯಕ. {district} ಪ್ರದೇಶದ ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಸಸ್ಯ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
            return f"Hello {farmer_name}! I am your AgriMitra AI Assistant. How can I assist your farming operations in {district}, {state} today?"

        if intent == "crop_declaration":
            if lang == "kn":
                return f"ಧನ್ಯವಾದಗಳು {farmer_name}. ನಾನು {crop} ಬೆಳೆಯ ವಿವರಗಳನ್ನು ಗುರುತಿಸಿದ್ದೇನೆ. {crop} ಬೆಳೆಗೆ ಯಾವ ಗೊಬ್ಬರ, ನೀರಾವರಿ, ರೋಗ ನಿರ್ವಹಣೆ ಅಥವಾ ಕೃಷಿ ಸಲಹೆ ಬೇಕು?"
            return f"Understood, {farmer_name}! I have set your current crop context to {crop}. How can I assist you with {crop} cultivation, fertilizer, irrigation, or pest management?"

        # If question requires a crop but crop is UNKNOWN, ask the farmer which crop!
        if crop is None and intent in ["fertilizer", "irrigation", "disease_treatment", "disease_prevention", "pest_management", "cultivation_general"]:
            if lang == "kn":
                return "ದಯವಿಟ್ಟು ನೀವು ಯಾವ ಬೆಳೆಯನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ ಎಂಬುದನ್ನು ತಿಳಿಸಿ (ಉದಾ: ಭತ್ತ, ಟೊಮೆಟೊ, ಮೆಕ್ಕೆಜೋಳ, ಮೆಣಸಿನಕಾಯಿ, ಕಡಲೆಕಾಯಿ, ರಾಗಿ, ಇತ್ಯಾದಿ)?"
            return "Could you please specify which crop you are growing? (e.g. Paddy, Tomato, Corn, Chilli, Groundnut, Ragi, Potato, etc.)"

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
            target_crop = crop or "Tomato"
            m = tool_data.get("market", {})
            prices = m.get("prices", {}) if m else {}

            if prices and isinstance(prices, dict) and ("avg_price" in prices or "modal_price" in prices):
                avg_price = prices.get("avg_price", prices.get("modal_price", 2200))
                min_p = prices.get("min_price", 1800)
                max_p = prices.get("max_price", 2500)
                if lang == "kn":
                    return f"{district} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {target_crop} ಪ್ರಸ್ತುತ ಬೆಲೆ ವಿವರ:\n• ಸರಾಸರಿ ಬೆಲೆ: ₹{avg_price}/ಕ್ವಿಂಟಾಲ್ (₹{round(avg_price/100, 1)}/ಕೆಜಿ)\n• ಬೆಲೆ ವ್ಯಾಪ್ತಿ: ₹{min_p} - ₹{max_p}/ಕ್ವಿಂಟಾಲ್\n\nಸಲಹೆ: 7-ದಿನಗಳ ಮುನ್ಸೂಚನೆಗಾಗಿ ಮಾರುಕಟ್ಟೆ ವಿಭಾಗವನ್ನು ವೀಕ್ಷಿಸಿ."
                return f"Current market prices for {target_crop} in {district} mandi:\n• Average Price: ₹{avg_price}/Quintal (₹{round(avg_price/100, 1)}/kg)\n• Price Range: ₹{min_p} - ₹{max_p}/Quintal\n\nTrend Note: Check the Market Prices tab for 7-day predictive analytics."
            else:
                if lang == "kn":
                    return f"{target_crop} ಬೆಳೆಗೆ ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ."
                return f"Live market price data for {target_crop} in {district} mandi is currently unavailable."

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
            target_crop = crop or "Crop"
            if lang == "kn":
                return (f"{target_crop} ಬೆಳೆ ರೋಗ ನಿರ್ವಹಣೆ ಮಾರ್ಗದರ್ಶನ:\n"
                        f"• ರೋಗ ಲಕ್ಷಣಗಳನ್ನು ಗಮನಿಸಿ: ಎಲೆ ಕಪ್ಪು ಕಲೆಗಳು ಅಥವಾ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿದರೆ ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ.\n"
                        f"• ಶಿಲೀಂಧ್ರನಾಶಕ: ಸೂಕ್ತ ತಾಮ್ರದ ಆಧಾರಿತ ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.\n"
                        f"• ತಡೆಗಟ್ಟುವಿಕೆ: ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ ಮತ್ತು ಹನಿ ನೀರಾವರಿ ಬಳಸಿ.\n\n"
                        f"ಗಮನಿಸಿ: ಎಲೆಯ ಫೋಟೋ ಮೂಲಕ ಸ್ವಯಂಚಾಲಿತ ಪತ್ತೆಗೆ 'ರೋಗ ಪತ್ತೆ' ವಿಭಾಗದಲ್ಲಿ ಟೊಮೆಟೊ ಮತ್ತು ಮೆಕ್ಕೆಜೋಳ ಬೆಂಬಲಿತವಾಗಿವೆ.")
            return (f"{target_crop} Disease Management Guidance:\n"
                    f"• Monitoring: Remove infected leaves at early onset to prevent spread.\n"
                    f"• Treatment: Apply recommended copper-based fungicide or mancozeb as per agricultural guidance.\n"
                    f"• Prevention: Practice crop rotation, ensure proper plant spacing, and avoid overhead leaf wetting.\n\n"
                    f"Note: Automated ML leaf photo analysis in the Disease Detection module currently supports Tomato and Corn.")

        if intent == "fertilizer":
            target_crop = crop or "Crop"
            if lang == "kn":
                return f"{target_crop} ಬೆಳೆಗೆ ಸಮತೋಲಿತ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ:\n• ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ: ಕಾಂಪೋಸ್ಟ್/ಸಗಣಿ ಗೊಬ್ಬರ (FYM) + NPK ಸಮತೋಲಿತ ಪ್ರಮಾಣ.\n• ಬೆಳವಣಿಗೆಯ ಹಂತದಲ್ಲಿ: ಯೂರಿಯಾ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.\n• ಸಾವಯವ: ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಜೀವಾಮೃತ ಬಳಸಿ."
            return f"Fertilizer Management for {target_crop}:\n• Basal Dose: Well-decomposed FYM/compost (10-12 tons/ha) + balanced NPK.\n• Top Dressing: Apply Nitrogen (Urea) and Potassium in 2-3 splits during growth stages.\n• Micronutrients: Spray Zinc Sulfate or Boron if leaf yellowing appears."

        if intent == "irrigation":
            target_crop = crop or "Crop"
            if lang == "kn":
                return f"{target_crop} ಬೆಳೆಗೆ ನೀರಾವರಿ ಮಾರ್ಗದರ್ಶನ:\n• ಹನಿ ನೀರಾವರಿ (Drip Irrigation) ಬಳಕೆಯಿಂದ ನೀರು ಉಳಿತಾಯ ಮತ್ತು ರೋಗ ತಡೆಗಟ್ಟಲು ಸಹಾಯವಾಗುತ್ತದೆ.\n• ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರು ಹಾಯಿಸಿ.\n• ಮಣ್ಣಿನ ತೇವಾಂಶ ಪರೀಕ್ಷಿಸಿ ಸೂಕ್ತ ಸಮಯದಲ್ಲಿ ನೀರು ನೀಡಿ."
            return f"Irrigation Recommendations for {target_crop}:\n• Drip Irrigation is highly recommended for water savings and reducing leaf dampness.\n• Water during early morning or late afternoon to minimize evaporation loss.\n• Maintain optimum soil moisture without waterlogging."

        if intent == "cultivation_general":
            target_crop = crop or "Crop"
            if lang == "kn":
                return f"{target_crop} ಬೆಳೆ ಕೃಷಿ ಮಾರ್ಗದರ್ಶನ:\n• ಮಣ್ಣು: ಫಲವತ್ತಾದ ಮಣ್ಣು ಮತ್ತು ಸರಿಯಾದ ನೀರು ಹರಿಯುವ ವ್ಯವಸ್ಥೆ.\n• ಬಿತ್ತನೆ: ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಸರಿಯಾದ ಅಂತರದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ.\n• ಪೋಷಕಾಂಶ: ಸಮತೋಲಿತ NPK ಮತ್ತು ಸಾವಯವ ಗೊಬ್ಬರ ಬಳಸಿ."
            return f"General Cultivation Guidelines for {target_crop}:\n• Soil Prep: Well-drained soil rich in organic matter.\n• Sowing: Use certified, disease-resistant seeds at recommended spacing.\n• Care: Maintain weed control, split fertilizer doses, and practice crop rotation."

        if intent == "help":
            if lang == "kn":
                return "ನಾನು ನಿಮಗೆ ಈ ವಿಷಯಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n1. 🌾 ಯಾವುದೇ ಬೆಳೆಗೆ ಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ಮಾರ್ಗದರ್ಶನ (ಭತ್ತ, ಟೊಮೆಟೊ, ಮೆಕ್ಕೆಜೋಳ, ಮೆಣಸಿನಕಾಯಿ, ಕಡಲೆಕಾಯಿ, ಇತ್ಯಾದಿ)\n2. 🌦️ ಹವಾಮಾನ ಮತ್ತು ಮುನ್ಸೂಚನೆ\n3. 💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು\n4. 🏛️ ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು\n5. 🦠 ಬೆಳೆ ರೋಗ ನಿರ್ವಹಣೆ"
            return "I can assist you with:\n1. 🌾 Crop cultivation, fertilizer & irrigation for ANY crop (Paddy, Tomato, Corn, Chilli, Groundnut, Ragi, etc.)\n2. 🌦️ Live weather forecasts & rain outlook\n3. 💰 Market prices & trends\n4. 🏛️ Government schemes & subsidy eligibility\n5. 🦠 Crop disease management guidance"

        # General Agriculture Default
        if lang == "kn":
            target = f"{crop} " if crop else ""
            return f"ಧನ್ಯವಾದಗಳು {farmer_name}! {district} ಪ್ರದೇಶದ {target}ಬೆಳೆ ನಿರ್ವಹಣೆ, ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಕೃಷಿ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಯಿದ್ದರೆ ಕೇಳಿ."
        target = f"{crop} " if crop else ""
        return f"Thank you for reaching out, {farmer_name}! Feel free to ask any specific questions about {target}cultivation, weather in {district}, market prices, or eligible government schemes."

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

            # Fetch live domain data if required by intent (NO weather leakage into non-weather queries)
            tool_data = {}
            if db and intent in ["weather", "market_price", "market_prediction", "government_scheme", "disease_information", "disease_treatment", "disease_prevention"]:
                tool_data = await self._fetch_tool_data(intent, crop, user_profile, db)

            # Attempt LLM API call (OpenAI primary, Gemini secondary)
            llm_response = await self._call_llm_api(clean_msg, intent, crop, lang, history, tool_data)

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
