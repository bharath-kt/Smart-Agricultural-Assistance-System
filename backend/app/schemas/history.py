"""Pydantic schemas for Farmer Activity History."""
from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime


class DiseaseHistoryItem(BaseModel):
    id: int
    crop_type: Optional[str] = None
    detected_disease: str
    confidence_score: float
    image_path: str
    alternative_diseases: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True


class SchemeHistoryItem(BaseModel):
    id: int
    scheme_id: Optional[int] = None
    scheme_name: Optional[str] = None
    search_query: Optional[str] = None
    action_type: str
    eligibility_status: Optional[str] = None
    details: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherHistoryItem(BaseModel):
    id: int
    location_name: str
    temperature: Optional[float] = None
    humidity: Optional[int] = None
    weather_condition: Optional[str] = None
    summary_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MarketHistoryItem(BaseModel):
    id: int
    crop_name: str
    state: Optional[str] = None
    district: Optional[str] = None
    market_name: Optional[str] = None
    modal_price: Optional[float] = None
    trend: Optional[str] = None
    summary_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogItem(BaseModel):
    id: int
    activity_type: str  # disease_detection, scheme_search, weather_view, market_query, profile_update
    title: str
    description: Optional[str] = None
    meta_data: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FarmerCombinedHistoryResponse(BaseModel):
    farmer_id: int
    disease_history: List[DiseaseHistoryItem]
    scheme_history: List[SchemeHistoryItem]
    weather_history: List[WeatherHistoryItem]
    market_history: List[MarketHistoryItem]
    recent_activities: List[ActivityLogItem]
