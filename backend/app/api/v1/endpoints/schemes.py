"""Government schemes API endpoints with eligibility recommendation engine."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user, get_optional_current_user
from app.services.scheme_service import scheme_service
from app.services.profile_service import profile_service
from app.services.history_service import history_service
from app.schemas.scheme import (
    SchemeResponse,
    SchemeDetailResponse,
    SchemeSearchRequest,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    SchemeRecommendationResponse
)

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])


@router.get("/recommendations", response_model=SchemeRecommendationResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run eligibility engine comparing logged-in farmer profile against government scheme rules."""
    profile = await profile_service.get_or_create_profile(db, current_user)
    recommendations = await scheme_service.recommend_schemes_for_farmer(db, profile)
    return recommendations


@router.get("", response_model=List[SchemeDetailResponse])
async def get_schemes(
    state: Optional[str] = Query(None, description="Filter by state"),
    farmer_type: Optional[str] = Query(None, description="Filter by farmer type"),
    crop: Optional[str] = Query(None, description="Filter by crop"),
    source: Optional[str] = Query(None, description="Filter by source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of government schemes with filtering."""
    schemes = await scheme_service.get_schemes(
        db=db,
        state=state,
        farmer_type=farmer_type,
        crop=crop,
        source=source,
        category=category,
        search=search,
        skip=skip,
        limit=limit
    )

    if current_user and (search or category or state):
        await history_service.log_scheme_activity(
            db=db,
            user_id=current_user.id,
            action_type="search",
            search_query=search or category or state,
            details={"results_count": len(schemes)}
        )

    return [scheme_service.format_scheme_detail(s) for s in schemes]


@router.get("/detail/{scheme_id}", response_model=SchemeDetailResponse)
async def get_scheme_by_id(
    scheme_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific scheme."""
    scheme = await scheme_service.get_scheme_by_id(db, scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheme not found"
        )

    if current_user:
        await history_service.log_scheme_activity(
            db=db,
            user_id=current_user.id,
            scheme_id=scheme.id,
            scheme_name=scheme.name,
            action_type="view"
        )

    return scheme_service.format_scheme_detail(scheme)


@router.get("/{scheme_id}", response_model=SchemeDetailResponse)
async def get_scheme_by_id_legacy(
    scheme_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed scheme (legacy path)."""
    return await get_scheme_by_id(scheme_id=scheme_id, current_user=current_user, db=db)


@router.get("/search/query", response_model=List[SchemeDetailResponse])
async def search_schemes(
    query: str = Query(..., min_length=2, description="Search query"),
    state: Optional[str] = Query(None, description="Filter by state"),
    crop: Optional[str] = Query(None, description="Filter by crop"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search schemes by text query."""
    schemes = await scheme_service.search_schemes(db=db, query_text=query, state=state, crop=crop)
    if current_user:
        await history_service.log_scheme_activity(
            db=db,
            user_id=current_user.id,
            action_type="search",
            search_query=query
        )
    return [scheme_service.format_scheme_detail(s) for s in schemes]


@router.post("/search", response_model=List[SchemeDetailResponse])
async def search_schemes_post(
    request: SchemeSearchRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search schemes by text query (POST method)."""
    schemes = await scheme_service.search_schemes(db=db, query_text=request.query, state=request.state, crop=request.crop)
    if current_user:
        await history_service.log_scheme_activity(
            db=db,
            user_id=current_user.id,
            action_type="search",
            search_query=request.query
        )
    return [scheme_service.format_scheme_detail(s) for s in schemes]


@router.post("/eligibility", response_model=EligibilityCheckResponse)
async def check_eligibility(
    request: EligibilityCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check eligibility for a scheme."""
    scheme = await scheme_service.get_scheme_by_id(db, request.scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheme not found"
        )

    # Use eligibility evaluation
    reasons = []
    missing_docs = scheme_service.parse_json_list(scheme.required_documents)
    is_eligible = True

    states = scheme_service.parse_json_list(scheme.eligible_states)
    if "All States" not in states and scheme.state != "All States" and request.state not in states:
        is_eligible = False
        reasons.append(f"Not available in {request.state}")

    farmer_types = scheme_service.parse_json_list(scheme.eligible_farmer_types)
    if "All Farmers" not in farmer_types and request.farmer_type not in farmer_types:
        is_eligible = False
        reasons.append(f"Requires farmer category: {', '.join(farmer_types)}")

    if scheme.max_land_holding and request.land_holding and request.land_holding > scheme.max_land_holding:
        is_eligible = False
        reasons.append(f"Land holding exceeds maximum of {scheme.max_land_holding} Ha")

    status_str = "Eligible" if is_eligible else "Not eligible"

    if current_user:
        await history_service.log_scheme_activity(
            db=db,
            user_id=current_user.id,
            scheme_id=scheme.id,
            scheme_name=scheme.name,
            action_type="eligibility_check",
            eligibility_status=status_str
        )

    return EligibilityCheckResponse(
        scheme_id=scheme.id,
        scheme_name=scheme.name,
        is_eligible=is_eligible,
        status=status_str,
        reasons=reasons,
        missing_documents=missing_docs
    )


@router.get("/sources/list", response_model=List[str])
async def get_scheme_sources():
    return ["PM-KISAN", "PMFBY", "eNAM", "KCC", "SMAM", "PMKSY", "SHC", "Karnataka State Govt"]


@router.get("/categories/list", response_model=List[str])
async def get_scheme_categories():
    return ["financial", "subsidy", "insurance", "loan", "equipment", "training"]
