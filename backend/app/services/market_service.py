"""Market price service for Agmarknet integration and ML prediction."""
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
import json
import httpx
import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.cache import cache

logger = get_logger(__name__)


class MarketService:
    """Service for market price data and predictions."""

    AGMARKNET_BASE_URL = "https://agmarknet.gov.in/"

    SUPPORTED_CROPS = [
        "Corn", "Coconut", "Onion", "Ginger", "Tomato",
        "Potato", "Rice", "Wheat", "Banana", "Chilli",
        "Turmeric", "Sugarcane", "Groundnut"
    ]

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self._model = None
    
    async def get_historical_prices(
        self,
        crop_name: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical market prices with filtering."""
        # Build cache key
        cache_key = f"market:prices:{crop_name}:{state}:{district}:{from_date}:{to_date}"
        
        cached = await cache.get_json(cache_key)
        if cached:
            return cached[:limit]
        
        # In production, this would query the database
        # For now, return mock data
        mock_data = self._generate_mock_prices(crop_name, state, district, limit)
        
        # Cache for 1 hour
        await cache.set_json(cache_key, mock_data, expire=3600)
        
        return mock_data[:limit]
    
    def _generate_mock_prices(
        self,
        crop_name: Optional[str],
        state: Optional[str],
        district: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate mock price data for demonstration."""
        crops = [crop_name] if crop_name else self.SUPPORTED_CROPS
        states = [state] if state else ["Karnataka", "Maharashtra", "Punjab", "Gujarat", "Tamil Nadu"]

        prices = []
        base_date = date.today() - timedelta(days=30)

        for i in range(limit):
            current_date = base_date + timedelta(days=i)
            crop = crops[i % len(crops)]
            st = states[i % len(states)]

            # Generate realistic Indian market price ranges (per Quintal)
            base_prices = {
                "Corn": 1800, "Coconut": 2500, "Onion": 1500,
                "Ginger": 8000, "Tomato": 2500, "Potato": 1200,
                "Rice": 2500, "Wheat": 2200, "Banana": 1800,
                "Chilli": 12000, "Turmeric": 9000, "Sugarcane": 350,
                "Groundnut": 5500
            }
            base = base_prices.get(crop, 2000)
            variation = np.random.uniform(-0.12, 0.12)
            modal = base * (1 + variation)

            prices.append({
                "id": i + 1,
                "crop_name": crop,
                "variety": "Local",
                "state": st,
                "district": district or f"District_{i % 5}",
                "market_name": f"Market_{i % 10}",
                "min_price": round(modal * 0.9, 2),
                "max_price": round(modal * 1.1, 2),
                "modal_price": round(modal, 2),
                "arrival_quantity": round(np.random.uniform(10, 500), 2),
                "unit": "Quintal",
                "price_date": current_date.isoformat(),
                "source": "Agmarknet"
            })

        return prices
    
    async def predict_price(
        self,
        crop_name: str,
        state: str,
        district: str,
        prediction_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """Predict market price using ML model."""
        if prediction_date is None:
            prediction_date = date.today() + timedelta(days=7)
        
        cache_key = f"market:predict:{crop_name}:{state}:{district}:{prediction_date}"
        
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
        
        try:
            # Load or train model if needed
            prediction = await self._run_prediction(
                crop_name, state, district, prediction_date
            )
            
            # Cache for 6 hours
            await cache.set_json(cache_key, prediction, expire=21600)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Price prediction error: {e}")
            return None
    
    async def _run_prediction(
        self,
        crop_name: str,
        state: str,
        district: str,
        prediction_date: date
    ) -> Dict[str, Any]:
        """Run ML prediction (simplified for demonstration)."""
        # Get historical data
        historical = await self.get_historical_prices(
            crop_name=crop_name,
            state=state,
            district=district,
            limit=30
        )

        if not historical:
            # Fallback to default prediction
            base_prices = {
                "Corn": 1800, "Coconut": 2500, "Onion": 1500,
                "Ginger": 8000, "Tomato": 2500, "Potato": 1200,
                "Rice": 2500, "Wheat": 2200, "Banana": 1800,
                "Chilli": 12000, "Turmeric": 9000, "Sugarcane": 350,
                "Groundnut": 5500
            }
            base = base_prices.get(crop_name, 2000)
            return {
                "crop_name": crop_name,
                "state": state,
                "district": district,
                "current_price": base,
                "predicted_price": base,
                "forecast_7d": [round(base * (1 + np.random.uniform(-0.05, 0.05)), 2) for _ in range(7)],
                "trend": "stable",
                "confidence_lower": round(base * 0.85, 2),
                "confidence_upper": round(base * 1.15, 2),
                "confidence_score": 0.7,
                "prediction_for_date": prediction_date.isoformat(),
                "prediction_made_at": datetime.utcnow().isoformat()
            }

        # Calculate trend
        prices = [p["modal_price"] for p in historical]
        avg_price = np.mean(prices)
        std_price = np.std(prices)
        current_price = prices[0] if prices else avg_price

        # Simple trend detection
        if len(prices) >= 7:
            recent_avg = np.mean(prices[-7:])
            older_avg = np.mean(prices[:-7]) if len(prices) > 7 else recent_avg
            trend_pct = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            trend_pct = 0

        # Determine trend direction
        if trend_pct > 0.02:
            trend = "increase"
        elif trend_pct < -0.02:
            trend = "decrease"
        else:
            trend = "stable"

        # Predict with trend
        days_ahead = (prediction_date - date.today()).days
        predicted = avg_price * (1 + trend_pct * (days_ahead / 30))

        # Generate 7-day forecast
        forecast_7d = []
        for day in range(1, 8):
            day_pred = avg_price * (1 + trend_pct * (day / 30))
            noise = np.random.uniform(-0.03, 0.03) * avg_price
            forecast_7d.append(round(day_pred + noise, 2))

        return {
            "crop_name": crop_name,
            "state": state,
            "district": district,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted, 2),
            "forecast_7d": forecast_7d,
            "trend": trend,
            "confidence_lower": round(predicted - 1.96 * std_price, 2),
            "confidence_upper": round(predicted + 1.96 * std_price, 2),
            "confidence_score": round(max(0.5, 1 - std_price / avg_price), 2),
            "prediction_for_date": prediction_date.isoformat(),
            "prediction_made_at": datetime.utcnow().isoformat()
        }
    
    async def get_market_trends(
        self,
        crop_name: str,
        state: str,
        district: str
    ) -> Optional[Dict[str, Any]]:
        """Get market trends for a crop."""
        historical = await self.get_historical_prices(
            crop_name=crop_name,
            state=state,
            district=district,
            limit=30
        )
        
        if not historical:
            return None
        
        prices = [p["modal_price"] for p in historical]
        current = prices[0]
        avg_7d = np.mean(prices[:7]) if len(prices) >= 7 else current
        avg_30d = np.mean(prices) if len(prices) >= 30 else np.mean(prices)
        
        change_7d = ((current - avg_7d) / avg_7d * 100) if avg_7d > 0 else 0
        change_30d = ((current - avg_30d) / avg_30d * 100) if avg_30d > 0 else 0
        
        if change_7d > 2:
            trend = "up"
        elif change_7d < -2:
            trend = "down"
        else:
            trend = "stable"
        
        return {
            "crop_name": crop_name,
            "state": state,
            "district": district,
            "current_price": current,
            "price_change_7d": round(change_7d, 2),
            "price_change_30d": round(change_30d, 2),
            "trend": trend,
            "average_price": round(avg_30d, 2)
        }
    
    async def fetch_agmarknet_data(self, date_from: date, date_to: date) -> List[Dict]:
        """Fetch data from Agmarknet API."""
        # This would integrate with the actual Agmarknet API
        # For now, return empty list
        logger.info(f"Fetching Agmarknet data from {date_from} to {date_to}")
        return []


# Global service instance
market_service = MarketService()
