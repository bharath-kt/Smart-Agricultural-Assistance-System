"""Farmer activity history service."""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete

from app.models.user import User
from app.models.disease import DiseaseDetection
from app.models.scheme import SchemeSearchHistory
from app.models.history import UserWeatherHistory, UserMarketHistory, UserActivityLog
from app.schemas.history import (
    DiseaseHistoryItem,
    SchemeHistoryItem,
    WeatherHistoryItem,
    MarketHistoryItem,
    ActivityLogItem,
    FarmerCombinedHistoryResponse
)


class HistoryService:
    """Service to track and retrieve farmer activities."""

    async def log_activity(
        self,
        db: AsyncSession,
        user_id: int,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None
    ) -> UserActivityLog:
        log = UserActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=description,
            meta_data=json.dumps(meta_data) if meta_data else None
        )
        db.add(log)
        await db.commit()
        return log

    async def log_weather_view(
        self,
        db: AsyncSession,
        user_id: int,
        location: str,
        temp: Optional[float] = None,
        humidity: Optional[int] = None,
        condition: Optional[str] = None
    ) -> UserWeatherHistory:
        record = UserWeatherHistory(
            user_id=user_id,
            location_name=location,
            temperature=temp,
            humidity=humidity,
            weather_condition=condition,
            summary_text=f"Checked weather for {location}: {condition or 'Forecast'}, Temp: {temp}°C" if temp else f"Checked weather for {location}"
        )
        db.add(record)
        await self.log_activity(
            db=db,
            user_id=user_id,
            activity_type="weather_view",
            title=f"Weather Checked ({location})",
            description=record.summary_text
        )
        return record

    async def log_market_query(
        self,
        db: AsyncSession,
        user_id: int,
        crop_name: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        modal_price: Optional[float] = None,
        trend: Optional[str] = "Stable"
    ) -> UserMarketHistory:
        record = UserMarketHistory(
            user_id=user_id,
            crop_name=crop_name,
            state=state,
            district=district,
            modal_price=modal_price,
            trend=trend,
            summary_text=f"Queried market price for {crop_name}: Rs. {modal_price}/quintal ({trend} trend)" if modal_price else f"Queried market price for {crop_name}"
        )
        db.add(record)
        await self.log_activity(
            db=db,
            user_id=user_id,
            activity_type="market_query",
            title=f"Market Price Searched ({crop_name})",
            description=record.summary_text
        )
        return record

    async def log_scheme_activity(
        self,
        db: AsyncSession,
        user_id: int,
        scheme_id: Optional[int] = None,
        scheme_name: Optional[str] = None,
        search_query: Optional[str] = None,
        action_type: str = "search",
        eligibility_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> SchemeSearchHistory:
        record = SchemeSearchHistory(
            user_id=user_id,
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            search_query=search_query,
            action_type=action_type,
            eligibility_status=eligibility_status,
            details=json.dumps(details) if details else None
        )
        db.add(record)
        title = f"Government Scheme {action_type.capitalize()}"
        if scheme_name:
            desc = f"{title}: {scheme_name} (Status: {eligibility_status or 'Viewed'})"
        else:
            desc = f"Searched schemes for '{search_query or 'All'}'"

        await self.log_activity(
            db=db,
            user_id=user_id,
            activity_type="scheme_search",
            title=title,
            description=desc
        )
        return record

    async def get_disease_history(self, db: AsyncSession, user_id: int, limit: int = 50) -> List[DiseaseHistoryItem]:
        query = select(DiseaseDetection).where(DiseaseDetection.user_id == user_id).order_by(desc(DiseaseDetection.created_at)).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        res = []
        for item in items:
            alts = []
            if item.alternative_diseases:
                try:
                    alts = json.loads(item.alternative_diseases)
                except Exception:
                    alts = []
            res.append(DiseaseHistoryItem(
                id=item.id,
                crop_type=item.crop_type,
                detected_disease=item.detected_disease,
                confidence_score=item.confidence_score,
                image_path=item.image_path,
                alternative_diseases=alts,
                created_at=item.created_at
            ))
        return res

    async def get_scheme_history(self, db: AsyncSession, user_id: int, limit: int = 50) -> List[SchemeHistoryItem]:
        query = select(SchemeSearchHistory).where(SchemeSearchHistory.user_id == user_id).order_by(desc(SchemeSearchHistory.created_at)).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        res = []
        for item in items:
            dt = None
            if item.details:
                try:
                    dt = json.loads(item.details)
                except Exception:
                    dt = item.details
            res.append(SchemeHistoryItem(
                id=item.id,
                scheme_id=item.scheme_id,
                scheme_name=item.scheme_name,
                search_query=item.search_query,
                action_type=item.action_type,
                eligibility_status=item.eligibility_status,
                details=dt,
                created_at=item.created_at
            ))
        return res

    async def get_weather_history(self, db: AsyncSession, user_id: int, limit: int = 50) -> List[WeatherHistoryItem]:
        query = select(UserWeatherHistory).where(UserWeatherHistory.user_id == user_id).order_by(desc(UserWeatherHistory.created_at)).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        return [WeatherHistoryItem.model_validate(i) for i in items]

    async def get_market_history(self, db: AsyncSession, user_id: int, limit: int = 50) -> List[MarketHistoryItem]:
        query = select(UserMarketHistory).where(UserMarketHistory.user_id == user_id).order_by(desc(UserMarketHistory.created_at)).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        return [MarketHistoryItem.model_validate(i) for i in items]

    async def get_combined_history(self, db: AsyncSession, user_id: int) -> FarmerCombinedHistoryResponse:
        disease_list = await self.get_disease_history(db, user_id, limit=20)
        scheme_list = await self.get_scheme_history(db, user_id, limit=20)
        weather_list = await self.get_weather_history(db, user_id, limit=20)
        market_list = await self.get_market_history(db, user_id, limit=20)

        query_act = select(UserActivityLog).where(UserActivityLog.user_id == user_id).order_by(desc(UserActivityLog.created_at)).limit(30)
        res_act = await db.execute(query_act)
        acts = res_act.scalars().all()
        act_items = []
        for a in acts:
            md = None
            if a.meta_data:
                try:
                    md = json.loads(a.meta_data)
                except Exception:
                    md = a.meta_data
            act_items.append(ActivityLogItem(
                id=a.id,
                activity_type=a.activity_type,
                title=a.title,
                description=a.description,
                meta_data=md,
                created_at=a.created_at
            ))

        return FarmerCombinedHistoryResponse(
            farmer_id=user_id,
            disease_history=disease_list,
            scheme_history=scheme_list,
            weather_history=weather_list,
            market_history=market_list,
            recent_activities=act_items
        )

    async def delete_all_history(self, db: AsyncSession, user_id: int) -> int:
        """Clear all history items belonging exclusively to the specified user_id."""
        total_deleted = 0
        for model in [UserActivityLog, DiseaseDetection, SchemeSearchHistory, UserWeatherHistory, UserMarketHistory]:
            res = await db.execute(delete(model).where(model.user_id == user_id))
            total_deleted += res.rowcount or 0
        await db.commit()
        return total_deleted

    async def delete_disease_history_item(self, db: AsyncSession, user_id: int, item_id: int) -> bool:
        """Delete a single disease detection history item owned by user_id."""
        result = await db.execute(select(DiseaseDetection).where(DiseaseDetection.id == item_id, DiseaseDetection.user_id == user_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    async def delete_scheme_history_item(self, db: AsyncSession, user_id: int, item_id: int) -> bool:
        """Delete a single scheme history item owned by user_id."""
        result = await db.execute(select(SchemeSearchHistory).where(SchemeSearchHistory.id == item_id, SchemeSearchHistory.user_id == user_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    async def delete_weather_history_item(self, db: AsyncSession, user_id: int, item_id: int) -> bool:
        """Delete a single weather history item owned by user_id."""
        result = await db.execute(select(UserWeatherHistory).where(UserWeatherHistory.id == item_id, UserWeatherHistory.user_id == user_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    async def delete_market_history_item(self, db: AsyncSession, user_id: int, item_id: int) -> bool:
        """Delete a single market history item owned by user_id."""
        result = await db.execute(select(UserMarketHistory).where(UserMarketHistory.id == item_id, UserMarketHistory.user_id == user_id))
        item = result.scalar_one_or_none()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True


history_service = HistoryService()
