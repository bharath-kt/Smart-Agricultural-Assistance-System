"""Market price model definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean

from app.db.base import Base


class MarketPrice(Base):
    """Historical market price model."""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Crop and location info
    crop_name = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    market_name = Column(String(255), nullable=True)
    
    # Price data
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=True)
    
    # Additional info
    arrival_quantity = Column(Float, nullable=True)  # in quintals
    unit = Column(String(20), default="Quintal")
    
    # Date
    price_date = Column(Date, nullable=False, index=True)
    
    # Source
    source = Column(String(100), default="Agmarknet")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class PricePrediction(Base):
    """Price prediction model."""
    __tablename__ = "price_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Prediction inputs
    crop_name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    
    # Prediction results
    predicted_price = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1
    
    # Prediction date
    prediction_for_date = Column(Date, nullable=False, index=True)
    prediction_made_at = Column(DateTime, default=datetime.utcnow)
    
    # Model info
    model_version = Column(String(50), nullable=True)
    
    # Actual price (for validation)
    actual_price = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)


class Crop(Base):
    """Crop reference data model."""
    __tablename__ = "crops"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=True)  # cereal, pulse, vegetable, etc.
    varieties = Column(String(1000), nullable=True)  # JSON array as string
    
    # Growing season info
    sowing_months = Column(String(100), nullable=True)
    harvesting_months = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
