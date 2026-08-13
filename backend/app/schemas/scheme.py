"""Government scheme Pydantic schemas."""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class SchemeBase(BaseModel):
    """Base scheme schema."""
    name: str
    short_description: Optional[str] = None


class SchemeResponse(SchemeBase):
    """Scheme response schema."""
    id: int
    scheme_code: str
    source: str
    government_level: Optional[str] = "Central"
    state: Optional[str] = "All States"
    department: Optional[str] = None
    ministry: Optional[str] = None
    category: Optional[str] = "subsidy"
    eligible_states: Optional[List[str]] = None
    eligible_farmer_types: Optional[List[str]] = None
    eligible_crops: Optional[List[str]] = None
    benefit_type: Optional[str] = None
    benefit_amount: Optional[str] = None
    application_url: Optional[str] = None
    official_website: Optional[str] = None
    helpline_number: Optional[str] = None
    is_active: bool = True
    last_updated_date: Optional[str] = None

    class Config:
        from_attributes = True


class SchemeDetailResponse(SchemeResponse):
    """Detailed scheme response schema."""
    full_description: Optional[str] = None
    benefit_description: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender_req: Optional[str] = "All"
    min_land_holding: Optional[float] = None
    max_land_holding: Optional[float] = None
    max_income: Optional[float] = None
    income_criteria: Optional[str] = None
    irrigation_req: Optional[str] = None
    eligibility_summary: Optional[str] = None
    required_documents: Optional[List[str]] = None
    application_process: Optional[str] = None
    offline_application_office: Optional[str] = None
    helpline_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[List[str]] = None


class SchemeRecommendationItem(BaseModel):
    scheme: SchemeDetailResponse
    status: str  # "Eligible", "Partially matching", "Not eligible"
    match_score: int  # 0 to 100
    match_reasons: List[str]
    missing_criteria: List[str]
    required_documents: List[str]
    disclaimer: str = "Final eligibility is subject to verification by the concerned government department."


class SchemeRecommendationResponse(BaseModel):
    farmer_id: int
    farmer_name: str
    total_schemes: int
    eligible_count: int
    partial_count: int
    not_eligible_count: int
    recommendations: List[SchemeRecommendationItem]
    disclaimer: str = "Recommendations are generated based on stored farmer profile information. Final approval is subject to verification by the concerned government department."


class SchemeFilter(BaseModel):
    """Scheme filter schema."""
    state: Optional[str] = None
    farmer_type: Optional[str] = None
    crop: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    search: Optional[str] = None


class SchemeSearchRequest(BaseModel):
    """Scheme search request schema."""
    query: str = Field(..., min_length=2)
    state: Optional[str] = None
    crop: Optional[str] = None


class SchemeApplicationCreate(BaseModel):
    """Scheme application creation schema."""
    scheme_id: int
    application_id: Optional[str] = None
    documents_submitted: Optional[List[str]] = None
    expected_completion: Optional[date] = None


class SchemeApplicationResponse(BaseModel):
    """Scheme application response schema."""
    id: int
    scheme_id: int
    scheme_name: str
    application_id: Optional[str]
    status: str
    status_notes: Optional[str]
    application_date: datetime
    last_updated: datetime
    benefit_received: bool
    benefit_amount_received: Optional[float]
    
    class Config:
        from_attributes = True


class EligibilityCheckRequest(BaseModel):
    """Eligibility check request schema."""
    scheme_id: int
    state: str
    farmer_type: str
    land_holding: Optional[float] = None
    crops: Optional[List[str]] = None


class EligibilityCheckResponse(BaseModel):
    """Eligibility check response schema."""
    scheme_id: int
    scheme_name: str
    is_eligible: bool
    status: str  # "Eligible", "Partially matching", "Not eligible"
    reasons: List[str]
    missing_documents: List[str]
