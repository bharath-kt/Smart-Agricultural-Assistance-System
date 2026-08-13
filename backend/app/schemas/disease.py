"""Disease detection Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DiseaseDetectionRequest(BaseModel):
    """Disease detection request schema."""
    crop_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AlternativeDisease(BaseModel):
    """Alternative disease prediction schema."""
    disease_name: str
    confidence: float


class DiseaseDetectionResponse(BaseModel):
    """Disease detection response schema."""
    detected_disease: str
    confidence_score: float
    alternative_predictions: List[AlternativeDisease]
    treatment: 'DiseaseTreatment'
    detected_at: datetime


class DiseaseTreatment(BaseModel):
    """Disease treatment schema."""
    organic: Optional[str]
    chemical: Optional[str]
    preventive: Optional[str]


class DiseaseInfoBase(BaseModel):
    """Base disease info schema."""
    name: str
    scientific_name: Optional[str]
    common_names: Optional[List[str]]


class DiseaseInfoResponse(DiseaseInfoBase):
    """Disease info response schema."""
    id: int
    affected_crops: List[str]
    symptoms: str
    causes: Optional[str]
    organic_treatment: Optional[str]
    chemical_treatment: Optional[str]
    preventive_measures: Optional[str]
    image_urls: Optional[List[str]]
    
    class Config:
        from_attributes = True


class DetectionHistory(BaseModel):
    """Detection history schema."""
    id: int
    detected_disease: str
    confidence_score: float
    crop_type: Optional[str]
    created_at: datetime
    is_validated: bool
    
    class Config:
        from_attributes = True


# Update forward references
DiseaseDetectionResponse.update_forward_refs()
