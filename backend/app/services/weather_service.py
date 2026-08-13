"""Weather service for OpenWeatherMap integration."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.cache import cache

logger = get_logger(__name__)

# Local geocoding database for common Indian cities (fallback when API key missing or for fast lookup)
INDIA_CITIES = {
    # Major cities
    "new delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi", "country": "IN"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi", "country": "IN"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra", "country": "IN"},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "country": "IN"},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "country": "IN"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu", "country": "IN"},
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal", "country": "IN"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "country": "IN"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra", "country": "IN"},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat", "country": "IN"},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan", "country": "IN"},
    "lucknow": {"lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh", "country": "IN"},
    "kanpur": {"lat": 26.4499, "lon": 80.3319, "state": "Uttar Pradesh", "country": "IN"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra", "country": "IN"},
    "indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh", "country": "IN"},
    "thane": {"lat": 19.2183, "lon": 72.9781, "state": "Maharashtra", "country": "IN"},
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "state": "Madhya Pradesh", "country": "IN"},
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh", "country": "IN"},
    "vadodara": {"lat": 22.3072, "lon": 73.1812, "state": "Gujarat", "country": "IN"},
    "firozabad": {"lat": 27.1591, "lon": 78.3958, "state": "Uttar Pradesh", "country": "IN"},
    "ludhiana": {"lat": 30.9010, "lon": 75.8573, "state": "Punjab", "country": "IN"},
    "rajkot": {"lat": 22.3039, "lon": 70.8022, "state": "Gujarat", "country": "IN"},
    "agra": {"lat": 27.1767, "lon": 78.0081, "state": "Uttar Pradesh", "country": "IN"},
    "siliguri": {"lat": 26.7271, "lon": 88.3953, "state": "West Bengal", "country": "IN"},
    "durgapur": {"lat": 23.5204, "lon": 87.3119, "state": "West Bengal", "country": "IN"},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794, "state": "Chandigarh", "country": "IN"},
    "dehradun": {"lat": 30.3165, "lon": 78.0322, "state": "Uttarakhand", "country": "IN"},
    "gwalior": {"lat": 26.2183, "lon": 78.1828, "state": "Madhya Pradesh", "country": "IN"},
    "ranchi": {"lat": 23.3441, "lon": 85.3096, "state": "Jharkhand", "country": "IN"},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558, "state": "Tamil Nadu", "country": "IN"},
    "kochi": {"lat": 9.9312, "lon": 76.2673, "state": "Kerala", "country": "IN"},
    "ernakulam": {"lat": 9.9816, "lon": 76.2999, "state": "Kerala", "country": "IN"},
    "mysore": {"lat": 12.2958, "lon": 76.6394, "state": "Karnataka", "country": "IN"},
    "mysuru": {"lat": 12.2958, "lon": 76.6394, "state": "Karnataka", "country": "IN"},
    "hubli": {"lat": 15.3647, "lon": 75.1240, "state": "Karnataka", "country": "IN"},
    "hubballi": {"lat": 15.3647, "lon": 75.1240, "state": "Karnataka", "country": "IN"},
    "belgaum": {"lat": 15.8497, "lon": 74.4977, "state": "Karnataka", "country": "IN"},
    "belagavi": {"lat": 15.8497, "lon": 74.4977, "state": "Karnataka", "country": "IN"},
    "mangalore": {"lat": 12.9141, "lon": 74.8560, "state": "Karnataka", "country": "IN"},
    "mangaluru": {"lat": 12.9141, "lon": 74.8560, "state": "Karnataka", "country": "IN"},
    "gulbarga": {"lat": 17.3297, "lon": 76.8343, "state": "Karnataka", "country": "IN"},
    "kalaburagi": {"lat": 17.3297, "lon": 76.8343, "state": "Karnataka", "country": "IN"},
    "davanagere": {"lat": 14.4644, "lon": 75.9218, "state": "Karnataka", "country": "IN"},
    "bellary": {"lat": 15.1394, "lon": 76.9214, "state": "Karnataka", "country": "IN"},
    "ballari": {"lat": 15.1394, "lon": 76.9214, "state": "Karnataka", "country": "IN"},
    "bijapur": {"lat": 16.8302, "lon": 75.7100, "state": "Karnataka", "country": "IN"},
    "vijayapura": {"lat": 16.8302, "lon": 75.7100, "state": "Karnataka", "country": "IN"},
    "shimoga": {"lat": 13.9299, "lon": 75.5681, "state": "Karnataka", "country": "IN"},
    "shivamogga": {"lat": 13.9299, "lon": 75.5681, "state": "Karnataka", "country": "IN"},
    "tumkur": {"lat": 13.3392, "lon": 77.1140, "state": "Karnataka", "country": "IN"},
    "tumakuru": {"lat": 13.3392, "lon": 77.1140, "state": "Karnataka", "country": "IN"},
    "raichur": {"lat": 16.2076, "lon": 77.3463, "state": "Karnataka", "country": "IN"},
    "udupi": {"lat": 13.3409, "lon": 74.7421, "state": "Karnataka", "country": "IN"},
    "hassan": {"lat": 13.0068, "lon": 76.0996, "state": "Karnataka", "country": "IN"},
    "mandya": {"lat": 12.5222, "lon": 76.8973, "state": "Karnataka", "country": "IN"},
    "chikmagalur": {"lat": 13.3161, "lon": 75.7720, "state": "Karnataka", "country": "IN"},
    "chikkamagaluru": {"lat": 13.3161, "lon": 75.7720, "state": "Karnataka", "country": "IN"},
    "kolar": {"lat": 13.1360, "lon": 78.1298, "state": "Karnataka", "country": "IN"},
    "chitradurga": {"lat": 14.2306, "lon": 76.3988, "state": "Karnataka", "country": "IN"},
    "bagalkot": {"lat": 16.1850, "lon": 75.6954, "state": "Karnataka", "country": "IN"},
    "haveri": {"lat": 14.7937, "lon": 75.4045, "state": "Karnataka", "country": "IN"},
    "dharwad": {"lat": 15.4589, "lon": 75.0078, "state": "Karnataka", "country": "IN"},
    "gadag": {"lat": 15.4315, "lon": 75.6350, "state": "Karnataka", "country": "IN"},
    "koppal": {"lat": 15.3504, "lon": 76.1542, "state": "Karnataka", "country": "IN"},
    "yadgir": {"lat": 16.7708, "lon": 77.1376, "state": "Karnataka", "country": "IN"},
    "ramanagara": {"lat": 12.7150, "lon": 77.2816, "state": "Karnataka", "country": "IN"},
    "chamarajanagar": {"lat": 11.9264, "lon": 76.9397, "state": "Karnataka", "country": "IN"},
    "kodagu": {"lat": 12.3375, "lon": 75.8069, "state": "Karnataka", "country": "IN"},
    "coorg": {"lat": 12.3375, "lon": 75.8069, "state": "Karnataka", "country": "IN"},
    "madikeri": {"lat": 12.4244, "lon": 75.7382, "state": "Karnataka", "country": "IN"},
    "bangarpet": {"lat": 12.9900, "lon": 78.1790, "state": "Karnataka", "country": "IN"},
    "bantwal": {"lat": 12.8906, "lon": 75.0349, "state": "Karnataka", "country": "IN"},
    "puttur": {"lat": 12.7667, "lon": 75.2167, "state": "Karnataka", "country": "IN"},
    "sullia": {"lat": 12.5567, "lon": 75.3900, "state": "Karnataka", "country": "IN"},
    "karwar": {"lat": 14.8138, "lon": 74.1316, "state": "Karnataka", "country": "IN"},
    "sirsi": {"lat": 14.6190, "lon": 74.8357, "state": "Karnataka", "country": "IN"},
    "kumta": {"lat": 14.4275, "lon": 74.4199, "state": "Karnataka", "country": "IN"},
    "honnavar": {"lat": 14.2804, "lon": 74.4437, "state": "Karnataka", "country": "IN"},
    "siddapur": {"lat": 14.3500, "lon": 74.9000, "state": "Karnataka", "country": "IN"},
    "sagara": {"lat": 14.1670, "lon": 75.0400, "state": "Karnataka", "country": "IN"},
    "hosanagara": {"lat": 13.9150, "lon": 75.0667, "state": "Karnataka", "country": "IN"},
    "thirthahalli": {"lat": 13.6894, "lon": 75.2433, "state": "Karnataka", "country": "IN"},
    "sringeri": {"lat": 13.4167, "lon": 75.2500, "state": "Karnataka", "country": "IN"},
    "kundapura": {"lat": 13.6333, "lon": 74.6833, "state": "Karnataka", "country": "IN"},
    "byndoor": {"lat": 13.8667, "lon": 74.6333, "state": "Karnataka", "country": "IN"},
    "brahmana": {"lat": 14.7833, "lon": 74.7000, "state": "Karnataka", "country": "IN"},
    "ankola": {"lat": 14.6667, "lon": 74.3000, "state": "Karnataka", "country": "IN"},
    "gokarna": {"lat": 14.5500, "lon": 74.3167, "state": "Karnataka", "country": "IN"},
    "yellapur": {"lat": 14.9667, "lon": 74.7167, "state": "Karnataka", "country": "IN"},
    "mundgod": {"lat": 14.9667, "lon": 75.0333, "state": "Karnataka", "country": "IN"},
    "haliyal": {"lat": 15.3333, "lon": 74.7667, "state": "Karnataka", "country": "IN"},
    "ron": {"lat": 15.6667, "lon": 75.7333, "state": "Karnataka", "country": "IN"},
    "nargund": {"lat": 15.7167, "lon": 75.3833, "state": "Karnataka", "country": "IN"},
    "navalgund": {"lat": 15.5667, "lon": 75.3667, "state": "Karnataka", "country": "IN"},
    "kundgol": {"lat": 15.2500, "lon": 75.2500, "state": "Karnataka", "country": "IN"},
    "shiggaon": {"lat": 14.9833, "lon": 75.2333, "state": "Karnataka", "country": "IN"},
    "haveri": {"lat": 14.7937, "lon": 75.4045, "state": "Karnataka", "country": "IN"},
    "hirekerur": {"lat": 14.4500, "lon": 75.4000, "state": "Karnataka", "country": "IN"},
    "ranibennur": {"lat": 14.6167, "lon": 75.6333, "state": "Karnataka", "country": "IN"},
    "sandur": {"lat": 15.0167, "lon": 76.5500, "state": "Karnataka", "country": "IN"},
    "hadagali": {"lat": 15.2333, "lon": 76.1333, "state": "Karnataka", "country": "IN"},
    "hospet": {"lat": 15.2695, "lon": 76.3871, "state": "Karnataka", "country": "IN"},
    "hosapete": {"lat": 15.2695, "lon": 76.3871, "state": "Karnataka", "country": "IN"},
    "harapanahalli": {"lat": 14.7833, "lon": 75.9833, "state": "Karnataka", "country": "IN"},
    "kotturu": {"lat": 14.8167, "lon": 76.2167, "state": "Karnataka", "country": "IN"},
    "kurugodu": {"lat": 15.4667, "lon": 76.8333, "state": "Karnataka", "country": "IN"},
    "kanakagiri": {"lat": 15.5667, "lon": 76.4167, "state": "Karnataka", "country": "IN"},
    "gangavathi": {"lat": 15.4333, "lon": 76.5333, "state": "Karnataka", "country": "IN"},
    "kustagi": {"lat": 16.0000, "lon": 76.2000, "state": "Karnataka", "country": "IN"},
    "yelbarga": {"lat": 15.6167, "lon": 76.0167, "state": "Karnataka", "country": "IN"},
    "sindhnur": {"lat": 15.7833, "lon": 76.7500, "state": "Karnataka", "country": "IN"},
    "manvi": {"lat": 16.0000, "lon": 77.0500, "state": "Karnataka", "country": "IN"},
    "devadurga": {"lat": 16.4333, "lon": 76.9333, "state": "Karnataka", "country": "IN"},
    "lingasugur": {"lat": 16.1667, "lon": 76.5167, "state": "Karnataka", "country": "IN"},
    "shorapur": {"lat": 16.5167, "lon": 76.7500, "state": "Karnataka", "country": "IN"},
    "shahapur": {"lat": 16.7000, "lon": 76.8333, "state": "Karnataka", "country": "IN"},
    "afzalpur": {"lat": 17.2000, "lon": 76.3500, "state": "Karnataka", "country": "IN"},
    "alanda": {"lat": 17.5667, "lon": 76.8333, "state": "Karnataka", "country": "IN"},
    "chittapur": {"lat": 17.1167, "lon": 77.0833, "state": "Karnataka", "country": "IN"},
    "sedam": {"lat": 17.1833, "lon": 77.2833, "state": "Karnataka", "country": "IN"},
    "jevargi": {"lat": 17.0167, "lon": 76.7667, "state": "Karnataka", "country": "IN"},
    "yadgir": {"lat": 16.7708, "lon": 77.1376, "state": "Karnataka", "country": "IN"},
    "gurmitkal": {"lat": 16.8667, "lon": 77.4000, "state": "Karnataka", "country": "IN"},
    "krishna": {"lat": 15.5167, "lon": 75.0500, "state": "Karnataka", "country": "IN"},
    "challakere": {"lat": 14.3167, "lon": 76.6500, "state": "Karnataka", "country": "IN"},
    "molakalmuru": {"lat": 14.7167, "lon": 76.7333, "state": "Karnataka", "country": "IN"},
    "koratagere": {"lat": 13.5333, "lon": 77.2333, "state": "Karnataka", "country": "IN"},
    "sira": {"lat": 13.7500, "lon": 76.9000, "state": "Karnataka", "country": "IN"},
    "pavagada": {"lat": 14.1000, "lon": 77.2667, "state": "Karnataka", "country": "IN"},
    "madhugiri": {"lat": 13.6600, "lon": 77.2120, "state": "Karnataka", "country": "IN"},
    "gubbi": {"lat": 13.3100, "lon": 76.9400, "state": "Karnataka", "country": "IN"},
    "turuvekere": {"lat": 13.1630, "lon": 76.6710, "state": "Karnataka", "country": "IN"},
    "kunigal": {"lat": 13.0220, "lon": 77.0270, "state": "Karnataka", "country": "IN"},
    "nelamangala": {"lat": 13.0980, "lon": 77.3900, "state": "Karnataka", "country": "IN"},
    "doddaballapur": {"lat": 13.2950, "lon": 77.5400, "state": "Karnataka", "country": "IN"},
    "devanahalli": {"lat": 13.2460, "lon": 77.7110, "state": "Karnataka", "country": "IN"},
    "hoskote": {"lat": 13.0700, "lon": 77.8000, "state": "Karnataka", "country": "IN"},
    "anekal": {"lat": 12.7100, "lon": 77.6960, "state": "Karnataka", "country": "IN"},
    "magadi": {"lat": 12.9570, "lon": 77.2260, "state": "Karnataka", "country": "IN"},
    "malur": {"lat": 13.0030, "lon": 78.1260, "state": "Karnataka", "country": "IN"},
    "kolar": {"lat": 13.1360, "lon": 78.1298, "state": "Karnataka", "country": "IN"},
    "mulbagal": {"lat": 13.1667, "lon": 78.4000, "state": "Karnataka", "country": "IN"},
    "srinivaspur": {"lat": 13.3333, "lon": 78.2167, "state": "Karnataka", "country": "IN"},
    "chintamani": {"lat": 13.4000, "lon": 78.0500, "state": "Karnataka", "country": "IN"},
    "gowribidanur": {"lat": 13.5833, "lon": 77.5167, "state": "Karnataka", "country": "IN"},
    "sidlaghatta": {"lat": 13.4000, "lon": 77.8667, "state": "Karnataka", "country": "IN"},
    "bageshpur": {"lat": 13.9833, "lon": 75.7333, "state": "Karnataka", "country": "IN"},
    "hosanagara": {"lat": 13.9150, "lon": 75.0667, "state": "Karnataka", "country": "IN"},
    "tiptur": {"lat": 13.2560, "lon": 76.4780, "state": "Karnataka", "country": "IN"},
    "arsikere": {"lat": 13.3140, "lon": 76.2570, "state": "Karnataka", "country": "IN"},
    "kadur": {"lat": 13.5530, "lon": 76.0120, "state": "Karnataka", "country": "IN"},
    "tarikere": {"lat": 13.7100, "lon": 75.8140, "state": "Karnataka", "country": "IN"},
    "birur": {"lat": 13.5970, "lon": 75.9720, "state": "Karnataka", "country": "IN"},
    "koppa": {"lat": 13.5310, "lon": 75.3630, "state": "Karnataka", "country": "IN"},
    "narasimharajapura": {"lat": 13.6100, "lon": 75.5200, "state": "Karnataka", "country": "IN"},
    "mudigere": {"lat": 13.1333, "lon": 75.6333, "state": "Karnataka", "country": "IN"},
    "alur": {"lat": 12.9900, "lon": 75.9900, "state": "Karnataka", "country": "IN"},
    "sakleshpur": {"lat": 12.9400, "lon": 75.7800, "state": "Karnataka", "country": "IN"},
    "belthangady": {"lat": 12.9900, "lon": 75.3000, "state": "Karnataka", "country": "IN"},
    "moodabidri": {"lat": 13.0833, "lon": 74.9833, "state": "Karnataka", "country": "IN"},
    "mulki": {"lat": 13.1000, "lon": 74.8000, "state": "Karnataka", "country": "IN"},
    "kapu": {"lat": 13.2167, "lon": 74.5500, "state": "Karnataka", "country": "IN"},
    "hebri": {"lat": 13.4667, "lon": 74.9833, "state": "Karnataka", "country": "IN"},
    "karkala": {"lat": 13.2167, "lon": 74.9833, "state": "Karnataka", "country": "IN"},
    "brahmavar": {"lat": 13.4333, "lon": 74.7500, "state": "Karnataka", "country": "IN"},
    "padubidri": {"lat": 13.1500, "lon": 74.8000, "state": "Karnataka", "country": "IN"},
    "kaup": {"lat": 13.2167, "lon": 74.6667, "state": "Karnataka", "country": "IN"},
    "koteshwara": {"lat": 13.3333, "lon": 74.7500, "state": "Karnataka", "country": "IN"},
    "gangolli": {"lat": 13.6500, "lon": 74.6667, "state": "Karnataka", "country": "IN"},
    "ankola": {"lat": 14.6667, "lon": 74.3000, "state": "Karnataka", "country": "IN"},
    "kumta": {"lat": 14.4275, "lon": 74.4199, "state": "Karnataka", "country": "IN"},
    "siddapur": {"lat": 14.3500, "lon": 74.9000, "state": "Karnataka", "country": "IN"},
    "soraba": {"lat": 14.3833, "lon": 75.1000, "state": "Karnataka", "country": "IN"},
    "hosanagara": {"lat": 13.9150, "lon": 75.0667, "state": "Karnataka", "country": "IN"},
    "channagiri": {"lat": 14.0240, "lon": 75.9260, "state": "Karnataka", "country": "IN"},
    "harihar": {"lat": 14.5100, "lon": 75.8000, "state": "Karnataka", "country": "IN"},
    "jagalur": {"lat": 14.5167, "lon": 76.3500, "state": "Karnataka", "country": "IN"},
    "holmargi": {"lat": 15.2667, "lon": 76.3000, "state": "Karnataka", "country": "IN"},
    "kottur": {"lat": 14.8167, "lon": 76.2167, "state": "Karnataka", "country": "IN"},
}


class WeatherService:
    """Service for fetching and managing weather data."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def geocode_location(self, query: str) -> Optional[Dict[str, Any]]:
        """Geocode a city name or pincode to lat/lon coordinates.
        
        First checks local database, then falls back to OpenWeatherMap geocoding API.
        """
        query_clean = query.strip().lower()
        
        # Check if it looks like a pincode (6 digits in India)
        is_pincode = query_clean.isdigit() and len(query_clean) == 6
        
        # 1. Check local database for city names
        if not is_pincode:
            city_match = INDIA_CITIES.get(query_clean)
            if city_match:
                logger.info(f"Local geocoding match for '{query}': {city_match['lat']}, {city_match['lon']}")
                return {
                    "name": query.strip().title(),
                    "local_names": {},
                    "lat": city_match["lat"],
                    "lon": city_match["lon"],
                    "country": city_match.get("country", "IN"),
                    "state": city_match.get("state", ""),
                }
        
        # 2. Try OpenWeatherMap geocoding API if key is available
        if self.api_key:
            try:
                url = f"{self.GEO_URL}/direct"
                params = {
                    "q": f"{query},IN",
                    "limit": 5,
                    "appid": self.api_key,
                }
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    logger.info(f"OpenWeatherMap geocoding for '{query}': {result['lat']}, {result['lon']}")
                    return {
                        "name": result.get("name", query.strip().title()),
                        "local_names": result.get("local_names", {}),
                        "lat": result["lat"],
                        "lon": result["lon"],
                        "country": result.get("country", "IN"),
                        "state": result.get("state", ""),
                    }
            except httpx.HTTPError as e:
                logger.warning(f"Geocoding API error for '{query}': {e}")
            except Exception as e:
                logger.warning(f"Unexpected geocoding error for '{query}': {e}")
        
        # 3. If pincode and no match, fallback to approximate coordinates based on pincode region
        if is_pincode:
            lat, lon = self._pincode_to_approx_coords(query_clean)
            if lat and lon:
                logger.info(f"Pincode approximate geocoding for '{query}': {lat}, {lon}")
                return {
                    "name": f"Pincode {query.strip()}",
                    "local_names": {},
                    "lat": lat,
                    "lon": lon,
                    "country": "IN",
                    "state": "",
                }
        
        logger.warning(f"Could not geocode location: {query}")
        return None

    async def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """Reverse geocode latitude and longitude to location name."""
        # 1. Try OpenWeatherMap reverse geocoding API if key is available
        if self.api_key:
            try:
                url = f"{self.GEO_URL}/reverse"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "limit": 1,
                    "appid": self.api_key,
                }
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    name = result.get("name")
                    state = result.get("state", "")
                    country = result.get("country", "IN")
                    if name:
                        return {
                            "name": name,
                            "lat": lat,
                            "lon": lon,
                            "country": country,
                            "state": state
                        }
            except Exception as e:
                logger.warning(f"Reverse geocoding API error: {e}")

        # 2. Local nearest city lookup from INDIA_CITIES
        best_city = None
        min_dist_sq = float("inf")
        for city_name, info in INDIA_CITIES.items():
            d_sq = (lat - info["lat"]) ** 2 + (lon - info["lon"]) ** 2
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                best_city = (city_name, info)

        if best_city and min_dist_sq < 25.0:
            city_name, info = best_city
            formatted_name = city_name.title()
            return {
                "name": formatted_name,
                "lat": lat,
                "lon": lon,
                "country": info.get("country", "IN"),
                "state": info.get("state", "")
            }

        return {
            "name": f"Location ({lat:.2f}, {lon:.2f})",
            "lat": lat,
            "lon": lon,
            "country": "IN",
            "state": ""
        }
    
    def _pincode_to_approx_coords(self, pincode: str) -> tuple:
        """Convert Indian pincode to approximate coordinates.
        
        This is a rough estimation based on pincode ranges.
        """
        pc = int(pincode)
        
        # Karnataka pincodes: 560000-591999 (entire Karnataka)
        if 560000 <= pc <= 562999:
            # Bangalore region
            return (12.97 + random.uniform(-0.3, 0.3), 77.59 + random.uniform(-0.3, 0.3))
        elif 563000 <= pc <= 577999:
            # South Karnataka (Mysuru, Mangaluru, etc.)
            return (13.0 + random.uniform(-1.5, 1.5), 76.0 + random.uniform(-1.5, 1.5))
        elif 578000 <= pc <= 582999:
            # North Karnataka (Hubballi, Belagavi, etc.)
            return (16.0 + random.uniform(-1, 1), 76.0 + random.uniform(-1, 1))
        elif 583000 <= pc <= 584999:
            # East Karnataka (Vijayapura, Kalaburagi, etc.)
            return (15.5 + random.uniform(-1, 1), 77.0 + random.uniform(-1, 1))
        elif 585000 <= pc <= 591999:
            # Coastal Karnataka (Udupi, Dakshina Kannada, etc.)
            return (13.5 + random.uniform(-1, 1), 74.5 + random.uniform(-1, 1))
        # Maharashtra
        elif 400000 <= pc <= 445999:
            return (19.0 + random.uniform(-2, 2), 73.0 + random.uniform(-2, 2))
        # Tamil Nadu
        elif 600000 <= pc <= 643999:
            return (11.0 + random.uniform(-2, 2), 78.0 + random.uniform(-2, 2))
        # Kerala
        elif 670000 <= pc <= 695999:
            return (10.0 + random.uniform(-1.5, 1.5), 76.5 + random.uniform(-2, 2))
        # Andhra Pradesh / Telangana
        elif 500000 <= pc <= 535999:
            return (17.0 + random.uniform(-2, 2), 79.0 + random.uniform(-2, 2))
        # Delhi / NCR
        elif 110000 <= pc <= 110099:
            return (28.61 + random.uniform(-0.2, 0.2), 77.20 + random.uniform(-0.2, 0.2))
        # Gujarat
        elif 360000 <= pc <= 396999:
            return (22.5 + random.uniform(-2, 2), 72.0 + random.uniform(-2, 2))
        # Rajasthan
        elif 300000 <= pc <= 345999:
            return (26.5 + random.uniform(-2, 2), 73.0 + random.uniform(-2, 2))
        # Uttar Pradesh
        elif 200000 <= pc <= 285999:
            return (27.0 + random.uniform(-2, 2), 80.0 + random.uniform(-2, 2))
        # West Bengal
        elif 700000 <= pc <= 743999:
            return (22.5 + random.uniform(-2, 2), 88.0 + random.uniform(-2, 2))
        # Punjab / Haryana
        elif 120000 <= pc <= 160999:
            return (30.0 + random.uniform(-1.5, 1.5), 76.0 + random.uniform(-2, 2))
        # Madhya Pradesh
        elif 450000 <= pc <= 488999:
            return (23.5 + random.uniform(-2, 2), 78.0 + random.uniform(-2, 2))
        # Odisha
        elif 750000 <= pc <= 770999:
            return (20.5 + random.uniform(-1.5, 1.5), 85.5 + random.uniform(-1.5, 1.5))
        # Bihar
        elif 800000 <= pc <= 855999:
            return (25.5 + random.uniform(-2, 2), 86.0 + random.uniform(-2, 2))
        # Jharkhand
        elif 820000 <= pc <= 835999:
            return (23.5 + random.uniform(-1.5, 1.5), 85.5 + random.uniform(-1.5, 1.5))
        # Assam / North East
        elif 780000 <= pc <= 799999:
            return (26.0 + random.uniform(-2, 2), 92.0 + random.uniform(-2, 2))
        # Chhattisgarh
        elif 490000 <= pc <= 497999:
            return (21.5 + random.uniform(-1.5, 1.5), 82.0 + random.uniform(-1.5, 1.5))
        # Uttarakhand
        elif 240000 <= pc <= 263999:
            return (30.0 + random.uniform(-1.5, 1.5), 79.0 + random.uniform(-1.5, 1.5))
        # Himachal Pradesh
        elif 170000 <= pc <= 177999:
            return (31.8 + random.uniform(-1.5, 1.5), 77.0 + random.uniform(-1.5, 1.5))
        # Jammu & Kashmir / Ladakh
        elif 180000 <= pc <= 195999:
            return (34.0 + random.uniform(-2, 2), 75.5 + random.uniform(-2, 2))
        # Goa
        elif 400000 <= pc <= 403999:
            return (15.3 + random.uniform(-0.3, 0.3), 74.0 + random.uniform(-0.5, 0.5))
        
        # Default: return approximate center of India
        return (20.5937 + random.uniform(-3, 3), 78.9629 + random.uniform(-3, 3))
    
    def _generate_mock_weather(self, latitude: float, longitude: float, location_name: str) -> Dict[str, Any]:
        """Generate realistic mock weather data based on location."""
        # Seed random with coordinates for consistent results
        rng = random.Random(f"{latitude:.2f}_{longitude:.2f}_{datetime.utcnow().day}")
        
        # Determine climate zone based on latitude
        if latitude < 14.0:  # Deep south (Kerala, TN, South Karnataka)
            base_temp = 28.0
            base_humidity = 75
            climate = "tropical"
        elif latitude < 18.0:  # South-central (Karnataka, Andhra, Telangana)
            base_temp = 30.0
            base_humidity = 65
            climate = "semi_tropical"
        elif latitude < 24.0:  # Central India
            base_temp = 32.0
            base_humidity = 55
            climate = "subtropical"
        elif latitude < 30.0:  # North-central
            base_temp = 34.0
            base_humidity = 45
            climate = "semi_arid"
        else:  # North India
            base_temp = 36.0
            base_humidity = 40
            climate = "arid"
        
        # Coastal adjustment (lower temp, higher humidity)
        if longitude > 72.0 and longitude < 78.0 and latitude < 22.0:
            base_temp -= 2.0
            base_humidity += 10
        
        # Hill station adjustment (Karnataka hill stations)
        hill_stations = [
            "coorg", "kodagu", "madikeri", "chikmagalur", "chikkamagaluru", 
            "sakleshpur", "shimoga", "shivamogga", "hassan", "chamarajanagar",
            "udupi", "kodagu", "coorg", "madikeri", "sakleshpur"
        ]
        if location_name.lower() in hill_stations:
            base_temp -= 8.0
            base_humidity += 15
        
        temperature = round(base_temp + rng.uniform(-3, 3), 1)
        humidity = min(100, max(20, int(base_humidity + rng.uniform(-10, 10))))
        wind_speed = round(rng.uniform(3, 18), 1)
        
        # Weather conditions based on humidity and randomness
        weather_options = [
            ("Clear", "clear sky", "01d"),
            ("Clouds", "few clouds", "02d"),
            ("Clouds", "scattered clouds", "03d"),
            ("Clouds", "broken clouds", "04d"),
        ]
        
        if humidity > 70:
            weather_options.extend([
                ("Rain", "light rain", "10d"),
                ("Rain", "moderate rain", "10d"),
                ("Thunderstorm", "thunderstorm with light rain", "11d"),
            ])
        if humidity > 85:
            weather_options.extend([
                ("Rain", "heavy intensity rain", "10d"),
                ("Drizzle", "light intensity drizzle", "09d"),
            ])
        
        weather_main, weather_desc, icon = rng.choice(weather_options)
        
        return {
            "location": {
                "name": location_name,
                "country": "IN",
                "latitude": latitude,
                "longitude": longitude
            },
            "temperature": temperature,
            "feels_like": round(temperature + rng.uniform(-2, 3), 1),
            "humidity": humidity,
            "pressure": int(1013 + rng.uniform(-15, 15)),
            "wind_speed": wind_speed,
            "wind_direction": int(rng.uniform(0, 360)),
            "visibility": int(rng.uniform(8000, 10000)),
            "weather_main": weather_main,
            "weather_description": weather_desc,
            "weather_icon": icon,
            "timestamp": datetime.utcnow(),
            "source": "mock"
        }
    
    def _generate_mock_forecast(self, latitude: float, longitude: float, location_name: str, days: int = 5) -> Dict[str, Any]:
        """Generate realistic mock forecast data."""
        rng = random.Random(f"{latitude:.2f}_{longitude:.2f}_forecast")
        
        forecast_list = []
        base_date = datetime.utcnow().date()
        
        if latitude < 14.0:
            base_temp = 28.0
            base_humidity = 75
        elif latitude < 18.0:
            base_temp = 30.0
            base_humidity = 65
        elif latitude < 24.0:
            base_temp = 32.0
            base_humidity = 55
        elif latitude < 30.0:
            base_temp = 34.0
            base_humidity = 45
        else:
            base_temp = 36.0
            base_humidity = 40
        
        # Hill stations (Karnataka hill stations)
        hill_stations = [
            "coorg", "kodagu", "madikeri", "chikmagalur", "chikkamagaluru", 
            "sakleshpur", "shimoga", "shivamogga", "hassan", "chamarajanagar",
            "udupi", "kodagu", "coorg", "madikeri", "sakleshpur"
        ]
        if location_name.lower() in hill_stations:
            base_temp -= 8.0
            base_humidity += 15
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            temp_var = rng.uniform(-4, 4)
            temp_min = round(base_temp + temp_var - 3, 1)
            temp_max = round(base_temp + temp_var + 3, 1)
            humidity = min(100, max(20, int(base_humidity + rng.uniform(-15, 15))))
            wind = round(rng.uniform(3, 20), 1)
            
            weather_options = [
                ("Clear", "clear sky"),
                ("Clouds", "few clouds"),
                ("Clouds", "scattered clouds"),
                ("Clouds", "broken clouds"),
            ]
            if humidity > 65:
                weather_options.extend([
                    ("Rain", "light rain"),
                    ("Rain", "moderate rain"),
                ])
            if humidity > 80:
                weather_options.extend([
                    ("Thunderstorm", "thunderstorm with rain"),
                ])
            
            main, desc = rng.choice(weather_options)
            
            forecast_list.append({
                "date": date.isoformat(),
                "temperature_min": temp_min,
                "temperature_max": temp_max,
                "humidity": humidity,
                "wind_speed": wind,
                "precipitation_probability": round(max(0, (humidity - 50) / 50 * 100), 1),
                "weather_main": main,
                "weather_description": desc,
            })
        
        return {
            "location": {
                "name": location_name,
                "country": "IN",
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast_list,
            "generated_at": datetime.utcnow(),
            "source": "mock"
        }
    
    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float,
        location_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Fetch current weather for location."""
        cache_key = f"weather:current:{latitude:.3f}:{longitude:.3f}"
        
        # Check cache first
        cached = await cache.get_json(cache_key)
        if cached:
            logger.info("Returning cached weather data")
            return cached
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured, using mock data")
            mock_data = self._generate_mock_weather(latitude, longitude, location_name or "Unknown")
            await cache.set_json(cache_key, mock_data, expire=600)
            return mock_data
        
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                "location": {
                    "name": data.get("name", location_name),
                    "country": data.get("sys", {}).get("country"),
                    "latitude": data.get("coord", {}).get("lat"),
                    "longitude": data.get("coord", {}).get("lon")
                },
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "wind_direction": data.get("wind", {}).get("deg"),
                "visibility": data.get("visibility"),
                "weather_main": data["weather"][0]["main"],
                "weather_description": data["weather"][0]["description"],
                "weather_icon": data["weather"][0].get("icon"),
                "timestamp": datetime.utcnow(),
                "source": "openweathermap"
            }
            
            # Cache for 10 minutes
            await cache.set_json(cache_key, weather_data, expire=600)
            
            # Store in database (async background task)
            await self._store_weather_history(weather_data, latitude, longitude)
            
            return weather_data
            
        except httpx.HTTPError as e:
            logger.error(f"Weather API error: {e}, falling back to mock data")
            mock_data = self._generate_mock_weather(latitude, longitude, location_name or "Unknown")
            await cache.set_json(cache_key, mock_data, expire=600)
            return mock_data
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}, falling back to mock data")
            mock_data = self._generate_mock_weather(latitude, longitude, location_name or "Unknown")
            await cache.set_json(cache_key, mock_data, expire=600)
            return mock_data
    
    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float,
        days: int = 7,
        location_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Fetch weather forecast for location."""
        cache_key = f"weather:forecast:{latitude:.3f}:{longitude:.3f}:{days}"
        
        # Check cache first
        cached = await cache.get_json(cache_key)
        if cached:
            logger.info("Returning cached forecast data")
            return cached
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured, using mock forecast data")
            mock_data = self._generate_mock_forecast(latitude, longitude, location_name or "Unknown", days)
            await cache.set_json(cache_key, mock_data, expire=3600)
            return mock_data
        
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 3-hour intervals
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and aggregate forecast data
            forecast_list = self._process_forecast(data.get("list", []), days)
            
            forecast_data = {
                "location": {
                    "name": data.get("city", {}).get("name", location_name),
                    "country": data.get("city", {}).get("country"),
                    "latitude": data.get("city", {}).get("coord", {}).get("lat"),
                    "longitude": data.get("city", {}).get("coord", {}).get("lon")
                },
                "forecast": forecast_list,
                "generated_at": datetime.utcnow(),
                "source": "openweathermap"
            }
            
            # Cache for 1 hour
            await cache.set_json(cache_key, forecast_data, expire=3600)
            
            return forecast_data
            
        except httpx.HTTPError as e:
            logger.error(f"Forecast API error: {e}, falling back to mock data")
            mock_data = self._generate_mock_forecast(latitude, longitude, location_name or "Unknown", days)
            await cache.set_json(cache_key, mock_data, expire=3600)
            return mock_data
        except Exception as e:
            logger.error(f"Unexpected error fetching forecast: {e}, falling back to mock data")
            mock_data = self._generate_mock_forecast(latitude, longitude, location_name or "Unknown", days)
            await cache.set_json(cache_key, mock_data, expire=3600)
            return mock_data
    
    def _process_forecast(
        self, 
        forecast_list: List[Dict], 
        days: int
    ) -> List[Dict[str, Any]]:
        """Process raw forecast data into daily summaries."""
        from collections import defaultdict
        
        daily_data = defaultdict(lambda: {
            "temps": [],
            "humidity": [],
            "wind_speed": [],
            "weather": [],
            "precipitation": []
        })
        
        for item in forecast_list:
            date = datetime.fromtimestamp(item["dt"]).date()
            daily_data[date]["temps"].append(item["main"]["temp"])
            daily_data[date]["humidity"].append(item["main"]["humidity"])
            daily_data[date]["wind_speed"].append(item.get("wind", {}).get("speed", 0))
            daily_data[date]["weather"].append(item["weather"][0])
            daily_data[date]["precipitation"].append(item.get("pop", 0))
        
        result = []
        for date, data in sorted(daily_data.items())[:days]:
            # Get most common weather condition
            weather_counts = {}
            for w in data["weather"]:
                weather_counts[w["main"]] = weather_counts.get(w["main"], 0) + 1
            main_weather = max(weather_counts, key=weather_counts.get) if weather_counts else "Unknown"
            
            result.append({
                "date": date.isoformat(),
                "temperature_min": min(data["temps"]),
                "temperature_max": max(data["temps"]),
                "humidity": int(sum(data["humidity"]) / len(data["humidity"])),
                "wind_speed": sum(data["wind_speed"]) / len(data["wind_speed"]),
                "precipitation_probability": max(data["precipitation"]) * 100,
                "weather_main": main_weather,
                "weather_description": next(
                    (w["description"] for w in data["weather"] if w["main"] == main_weather),
                    ""
                )
            })
        
        return result
    
    async def _store_weather_history(
        self, 
        weather_data: Dict, 
        latitude: float, 
        longitude: float
    ):
        """Store weather data in database (called as background task)."""
        # This would be called via Celery in production
        pass
    
    async def check_alerts(
        self, 
        latitude: float, 
        longitude: float,
        weather_data: Dict
    ) -> List[Dict[str, Any]]:
        """Check for weather alerts based on conditions."""
        alerts = []
        
        temp = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        weather_main = weather_data.get("weather_main", "").lower()
        
        # High temperature alert
        if temp > 40:
            alerts.append({
                "type": "high_temp",
                "severity": "high",
                "title": "Extreme Heat Warning",
                "description": f"Temperature is {temp}°C. Take precautions to protect crops."
            })
        elif temp > 35:
            alerts.append({
                "type": "high_temp",
                "severity": "medium",
                "title": "High Temperature Alert",
                "description": f"Temperature is {temp}°C. Monitor crop water needs."
            })
        
        # Rain alert
        if "rain" in weather_main or "thunderstorm" in weather_main:
            alerts.append({
                "type": "rain",
                "severity": "medium",
                "title": "Rain Expected",
                "description": f"{weather_data.get('weather_description', 'Rain')} expected. Plan field work accordingly."
            })
        
        # Drought conditions (high temp + low humidity)
        if temp > 35 and humidity < 30:
            alerts.append({
                "type": "drought",
                "severity": "high",
                "title": "Drought Conditions",
                "description": "High temperature with low humidity. Increase irrigation."
            })
        
        return alerts


# Global service instance
weather_service = WeatherService()
