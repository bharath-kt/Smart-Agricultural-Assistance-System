"""Market price Pydantic schemas."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class MarketPriceBase(BaseModel):
    """Base market price schema."""
    crop_name: str
    state: str
    district: str


class MarketPriceCreate(MarketPriceBase):
    """Market price creation schema."""
    variety: Optional[str] = None
    market_name: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: Optional[float] = None
    arrival_quantity: Optional[float] = None
    price_date: date


class MarketPriceResponse(MarketPriceBase):
    """Market price response schema."""
    id: int
    variety: Optional[str]
    market_name: Optional[str]
    min_price: Optional[float]
    max_price: Optional[float]
    modal_price: Optional[float]
    arrival_quantity: Optional[float]
    unit: str
    price_date: date
    source: str
    
    class Config:
        from_attributes = True


class PriceFilter(BaseModel):
    """Price filter schema."""
    crop_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class PricePredictionRequest(BaseModel):
    """Price prediction request schema."""
    crop_name: str
    state: str
    district: str
    prediction_date: Optional[date] = None


class PricePredictionResponse(BaseModel):
    """Price prediction response schema."""
    crop_name: str
    state: str
    district: str
    current_price: Optional[float]
    predicted_price: float
    forecast_7d: Optional[List[float]]
    trend: Optional[str]
    confidence_lower: Optional[float]
    confidence_upper: Optional[float]
    confidence_score: Optional[float]
    prediction_for_date: date
    prediction_made_at: datetime


class CropBase(BaseModel):
    """Base crop schema."""
    name: str
    category: Optional[str] = None


class CropResponse(CropBase):
    """Crop response schema."""
    id: int
    varieties: Optional[List[str]]
    sowing_months: Optional[List[str]]
    harvesting_months: Optional[List[str]]
    
    class Config:
        from_attributes = True


class MarketTrend(BaseModel):
    """Market trend schema."""
    crop_name: str
    state: str
    district: str
    current_price: float
    price_change_7d: Optional[float]
    price_change_30d: Optional[float]
    trend: str  # up, down, stable
    average_price: float
