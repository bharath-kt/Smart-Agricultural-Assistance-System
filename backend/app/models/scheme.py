"""Government scheme model definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, ARRAY, Float, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from app.db.base import Base


class GovernmentScheme(Base):
    """Government scheme model."""
    __tablename__ = "government_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    scheme_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    short_description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    
    # Source & Department
    source = Column(String(100), nullable=False)  # PM-KISAN, PMFBY, eNAM, etc.
    government_level = Column(String(50), default="Central")  # Central, State
    state = Column(String(100), default="All States")
    department = Column(String(200), nullable=True)
    ministry = Column(String(200), nullable=True)
    category = Column(String(100), default="subsidy")  # subsidy, financial, loan, insurance, training, equipment
    
    # Eligibility rules
    eligible_states = Column(Text, nullable=True)  # JSON array or "All States"
    eligible_farmer_types = Column(Text, nullable=True)  # JSON array
    eligible_crops = Column(Text, nullable=True)  # JSON array or "All Crops"
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    gender_req = Column(String(20), default="All")  # All, Male, Female
    min_land_holding = Column(Float, nullable=True)  # in hectares
    max_land_holding = Column(Float, nullable=True)  # in hectares
    max_income = Column(Float, nullable=True)
    income_criteria = Column(String(255), nullable=True)
    irrigation_req = Column(String(100), nullable=True)
    eligibility_summary = Column(Text, nullable=True)
    
    # Benefits
    benefit_type = Column(String(100), nullable=True)  # financial, subsidy, insurance, etc.
    benefit_amount = Column(String(255), nullable=True)
    benefit_description = Column(Text, nullable=True)
    
    # Documents required
    required_documents = Column(Text, nullable=True)  # JSON array
    
    # Application process
    application_process = Column(Text, nullable=True)
    application_url = Column(String(500), nullable=True)
    offline_application_office = Column(String(500), nullable=True)
    
    # Contact info
    helpline_number = Column(String(50), nullable=True)
    helpline_email = Column(String(255), nullable=True)
    official_website = Column(String(500), nullable=True)
    
    # Validity
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    last_updated_date = Column(String(50), nullable=True)
    
    # Search tags
    tags = Column(Text, nullable=True)  # JSON array for search/filtering
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)


class SchemeSearchHistory(Base):
    """Scheme search and eligibility history model."""
    __tablename__ = "scheme_search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("government_schemes.id"), nullable=True)
    scheme_name = Column(String(500), nullable=True)
    search_query = Column(String(255), nullable=True)
    action_type = Column(String(50), default="search")  # search, view, recommendation
    eligibility_status = Column(String(50), nullable=True)  # Eligible, Partially matching, Not eligible
    details = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class SchemeApplication(Base):
    """User's scheme application tracking."""
    __tablename__ = "scheme_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("government_schemes.id"), nullable=False)
    
    # Application details
    application_id = Column(String(100), nullable=True)  # Government provided ID
    application_date = Column(DateTime, default=datetime.utcnow)
    
    # Status
    status = Column(String(50), default="applied")  # applied, under_review, approved, rejected, completed
    status_notes = Column(Text, nullable=True)
    
    # Documents submitted
    documents_submitted = Column(Text, nullable=True)  # JSON array
    
    # Updates
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expected_completion = Column(Date, nullable=True)
    
    # Benefits received
    benefit_received = Column(Boolean, default=False)
    benefit_amount_received = Column(Float, nullable=True)
    benefit_date = Column(DateTime, nullable=True)
