"""Farmer Activity History API Endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.history_service import history_service
from app.schemas.history import (
    DiseaseHistoryItem,
    SchemeHistoryItem,
    WeatherHistoryItem,
    MarketHistoryItem,
    FarmerCombinedHistoryResponse
)

router = APIRouter(prefix="/history", tags=["Farmer Activity History"])


@router.get("/all", response_model=FarmerCombinedHistoryResponse)
async def get_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve complete combined activity history for logged-in farmer."""
    return await history_service.get_combined_history(db, current_user.id)


@router.delete("/all", status_code=status.HTTP_200_OK)
async def clear_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete all activity history belonging to the logged-in farmer."""
    deleted_count = await history_service.delete_all_history(db, current_user.id)
    return {"message": "All history deleted successfully", "deleted_count": deleted_count}


@router.get("/disease", response_model=List[DiseaseHistoryItem])
async def get_disease_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve disease detection history for logged-in farmer."""
    return await history_service.get_disease_history(db, current_user.id, limit=limit)


@router.delete("/disease/{item_id}", status_code=status.HTTP_200_OK)
async def delete_disease_history_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single disease detection history item owned by logged-in farmer."""
    success = await history_service.delete_disease_history_item(db, current_user.id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease history item not found or unauthorized"
        )
    return {"message": "Disease history item deleted successfully"}


@router.get("/schemes", response_model=List[SchemeHistoryItem])
async def get_scheme_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve government scheme search and recommendation history for logged-in farmer."""
    return await history_service.get_scheme_history(db, current_user.id, limit=limit)


@router.delete("/schemes/{item_id}", status_code=status.HTTP_200_OK)
async def delete_scheme_history_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single scheme history item owned by logged-in farmer."""
    success = await history_service.delete_scheme_history_item(db, current_user.id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheme history item not found or unauthorized"
        )
    return {"message": "Scheme history item deleted successfully"}


@router.get("/weather", response_model=List[WeatherHistoryItem])
async def get_weather_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve weather search history for logged-in farmer."""
    return await history_service.get_weather_history(db, current_user.id, limit=limit)


@router.delete("/weather/{item_id}", status_code=status.HTTP_200_OK)
async def delete_weather_history_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single weather history item owned by logged-in farmer."""
    success = await history_service.delete_weather_history_item(db, current_user.id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather history item not found or unauthorized"
        )
    return {"message": "Weather history item deleted successfully"}


@router.get("/market", response_model=List[MarketHistoryItem])
async def get_market_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve market price search history for logged-in farmer."""
    return await history_service.get_market_history(db, current_user.id, limit=limit)


@router.delete("/market/{item_id}", status_code=status.HTTP_200_OK)
async def delete_market_history_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single market history item owned by logged-in farmer."""
    success = await history_service.delete_market_history_item(db, current_user.id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market history item not found or unauthorized"
        )
    return {"message": "Market history item deleted successfully"}

