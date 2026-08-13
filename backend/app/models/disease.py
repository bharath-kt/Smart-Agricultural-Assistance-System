"""Disease detection model definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean

from app.db.base import Base


class DiseaseDetection(Base):
    """Disease detection record model."""
    __tablename__ = "disease_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Image info
    image_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=True)
    
    # Detection results
    detected_disease = Column(String(255), nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Additional predictions (top 3)
    alternative_diseases = Column(String(1000), nullable=True)  # JSON array
    
    # Crop info
    crop_type = Column(String(100), nullable=True)
    
    # Status
    is_validated = Column(Boolean, default=False)
    expert_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class DiseaseInfo(Base):
    """Disease information reference model."""
    __tablename__ = "disease_info"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Disease identification
    name = Column(String(255), unique=True, nullable=False)
    scientific_name = Column(String(255), nullable=True)
    common_names = Column(String(500), nullable=True)
    
    # Affected crops
    affected_crops = Column(String(500), nullable=False)  # JSON array
    
    # Disease info
    symptoms = Column(Text, nullable=False)
    causes = Column(Text, nullable=True)
    
    # Treatment
    organic_treatment = Column(Text, nullable=True)
    chemical_treatment = Column(Text, nullable=True)
    preventive_measures = Column(Text, nullable=True)
    
    # Additional resources
    image_urls = Column(String(1000), nullable=True)  # JSON array
    external_links = Column(String(1000), nullable=True)  # JSON array
    
    is_active = Column(Boolean, default=True)
