"""Market price API endpoints."""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.market_service import market_service
from app.schemas.market import (
    MarketPriceResponse,
    PricePredictionRequest,
    PricePredictionResponse,
    MarketTrend,
    CropResponse
)

from app.models.user import User
from app.core.security import get_optional_current_user
from app.services.history_service import history_service

router = APIRouter(prefix="/market", tags=["Market Prices"])


@router.get("/prices", response_model=List[MarketPriceResponse])
async def get_market_prices(
    crop_name: Optional[str] = Query(None, description="Crop name"),
    state: Optional[str] = Query(None, description="State"),
    district: Optional[str] = Query(None, description="District"),
    from_date: Optional[date] = Query(None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="To date (YYYY-MM-DD)"),
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical market prices with filtering."""
    prices = await market_service.get_historical_prices(
        crop_name=crop_name,
        state=state,
        district=district,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )

    if current_user and crop_name:
        modal_p = None
        if prices:
            p0 = prices[0]
            modal_p = p0.get("modal_price") if isinstance(p0, dict) else getattr(p0, "modal_price", None)
        await history_service.log_market_query(
            db=db,
            user_id=current_user.id,
            crop_name=crop_name,
            state=state,
            district=district,
            modal_price=float(modal_p) if modal_p is not None else None,
            trend="Stable"
        )
    
    return prices


@router.get("/prices/{crop_name}", response_model=List[MarketPriceResponse])
async def get_prices_by_crop(
    crop_name: str,
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(default=30, ge=1, le=365),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get market prices for a specific crop."""
    prices = await market_service.get_historical_prices(
        crop_name=crop_name,
        state=state,
        district=district,
        limit=limit
    )

    if current_user:
        modal_p = prices[0].modal_price if prices else None
        await history_service.log_market_query(
            db=db,
            user_id=current_user.id,
            crop_name=crop_name,
            state=state,
            district=district,
            modal_price=float(modal_p) if modal_p is not None else None,
            trend="Stable"
        )
    
    return prices


@router.get("/predict", response_model=PricePredictionResponse)
async def predict_price(
    crop_name: str = Query(..., description="Crop name"),
    state: str = Query(..., description="State"),
    district: str = Query(..., description="District"),
    prediction_date: Optional[date] = Query(None, description="Date to predict for (YYYY-MM-DD)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict market price for a crop."""
    if crop_name not in market_service.SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid crop '{crop_name}'. Supported crops: {', '.join(market_service.SUPPORTED_CROPS)}"
        )

    prediction = await market_service.predict_price(
        crop_name=crop_name,
        state=state,
        district=district,
        prediction_date=prediction_date
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to generate prediction"
        )

    if current_user:
        await history_service.log_market_query(
            db=db,
            user_id=current_user.id,
            crop_name=crop_name,
            state=state,
            district=district,
            modal_price=float(prediction.predicted_price),
            trend=prediction.trend
        )

    return prediction


@router.post("/predict", response_model=PricePredictionResponse)
async def predict_price_post(
    request: PricePredictionRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Predict market price for a crop (POST method)."""
    if request.crop_name not in market_service.SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid crop '{request.crop_name}'. Supported crops: {', '.join(market_service.SUPPORTED_CROPS)}"
        )

    prediction = await market_service.predict_price(
        crop_name=request.crop_name,
        state=request.state,
        district=request.district,
        prediction_date=request.prediction_date
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to generate prediction"
        )

    if current_user:
        await history_service.log_market_query(
            db=db,
            user_id=current_user.id,
            crop_name=request.crop_name,
            state=request.state,
            district=request.district,
            modal_price=float(prediction.predicted_price),
            trend=prediction.trend
        )

    return prediction


@router.get("/trends/{crop_name}", response_model=MarketTrend)
async def get_market_trends(
    crop_name: str,
    state: str = Query(..., description="State"),
    district: str = Query(..., description="District"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get market trends for a crop."""
    trends = await market_service.get_market_trends(
        crop_name=crop_name,
        state=state,
        district=district
    )
    
    if not trends:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data available for the specified crop and location"
        )

    if current_user:
        await history_service.log_market_query(
            db=db,
            user_id=current_user.id,
            crop_name=crop_name,
            state=state,
            district=district,
            modal_price=float(trends.current_price),
            trend=trends.trend
        )

    return trends


@router.get("/crops", response_model=List[CropResponse])
async def get_crops(
    category: Optional[str] = Query(None, description="Crop category filter"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available crops."""
    from sqlalchemy import select
    from app.models.market import Crop
    
    query = select(Crop).where(Crop.is_active == True)
    
    if category:
        query = query.where(Crop.category == category)
    
    result = await db.execute(query)
    crops = result.scalars().all()
    
    if not crops:
        default_crops = [
            {"id": 1, "name": "Corn", "category": "Cereal"},
            {"id": 2, "name": "Coconut", "category": "Cash Crop"},
            {"id": 3, "name": "Onion", "category": "Vegetable"},
            {"id": 4, "name": "Ginger", "category": "Spice"},
            {"id": 5, "name": "Tomato", "category": "Vegetable"},
            {"id": 6, "name": "Potato", "category": "Vegetable"},
            {"id": 7, "name": "Rice", "category": "Cereal"},
            {"id": 8, "name": "Wheat", "category": "Cereal"},
            {"id": 9, "name": "Banana", "category": "Fruit"},
            {"id": 10, "name": "Chilli", "category": "Spice"},
            {"id": 11, "name": "Turmeric", "category": "Spice"},
            {"id": 12, "name": "Sugarcane", "category": "Cash Crop"},
            {"id": 13, "name": "Groundnut", "category": "Oilseed"}
        ]
        return default_crops
    
    return crops
