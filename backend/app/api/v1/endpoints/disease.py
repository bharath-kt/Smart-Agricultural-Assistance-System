"""Disease detection API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.core.security import get_optional_current_user
from app.services.disease_service import disease_service
from app.schemas.disease import DetectionHistory
from app.core.logging import get_logger

router = APIRouter(prefix="/disease", tags=["Disease Detection"])
logger = get_logger(__name__)


@router.post("/detect", response_model=dict)
async def detect_disease(
    image: UploadFile = File(..., description="Leaf image for disease detection"),
    crop_type: Optional[str] = Form(None, description="Type of crop (Tomato, Corn, or Paddy)"),
    latitude: Optional[float] = Form(None, description="Latitude (optional)"),
    longitude: Optional[float] = Form(None, description="Longitude (optional)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect plant disease from leaf image. Supports Tomato, Corn, and Paddy."""
    if crop_type and crop_type not in disease_service.SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported plant '{crop_type}'. Upload Tomato, Corn, or Paddy leaf."
        )

    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    max_size = 10 * 1024 * 1024
    contents = await image.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB"
        )

    try:
        result = await disease_service.detect_disease(
            image_bytes=contents,
            crop_type=crop_type
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image"
            )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        from app.models.disease import DiseaseDetection
        from app.models.history import UserActivityLog
        import os

        upload_dir = "uploads/disease_images"
        os.makedirs(upload_dir, exist_ok=True)

        user_prefix = f"user_{current_user.id}" if current_user else "anonymous"
        filename = f"{user_prefix}_{image.filename}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        detection_record = DiseaseDetection(
            user_id=current_user.id if current_user else None,
            image_path=file_path,
            original_filename=image.filename,
            detected_disease=result["detected_disease"],
            confidence_score=result["confidence_score"],
            alternative_diseases=str(result["alternative_predictions"]),
            crop_type=crop_type
        )
        db.add(detection_record)

        if current_user:
            log = UserActivityLog(
                user_id=current_user.id,
                activity_type="disease_detection",
                title=f"Disease Detected ({crop_type or 'Leaf'})",
                description=f"Identified '{result['detected_disease']}' with {round(result['confidence_score']*100, 1)}% confidence."
            )
            db.add(log)

        await db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing image"
        )


@router.get("/info/{disease_name}", response_model=dict)
async def get_disease_info(disease_name: str):
    """Get detailed information about a disease."""
    info = await disease_service.get_disease_info(disease_name)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease information not found"
        )
    
    return info


@router.get("/history", response_model=List[DetectionHistory])
async def get_detection_history(
    limit: int = 10,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent disease detection history."""
    if not current_user:
        return []

    from sqlalchemy import select
    from app.models.disease import DiseaseDetection

    query = select(DiseaseDetection).where(DiseaseDetection.user_id == current_user.id)
    result = await db.execute(
        query.order_by(DiseaseDetection.created_at.desc()).limit(limit)
    )

    history = result.scalars().all()
    return history


@router.get("/diseases", response_model=List[str])
async def get_supported_diseases(crop_type: Optional[str] = None):
    """Get list of supported diseases (Tomato and Corn only)."""
    diseases = disease_service.DISEASE_CLASSES

    if crop_type:
        if crop_type not in disease_service.SUPPORTED_CROPS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported plant '{crop_type}'. Supported: {', '.join(disease_service.SUPPORTED_CROPS)}"
            )
        crop_lower = crop_type.lower()
        diseases = [
            d for d in diseases
            if crop_lower in d.lower()
        ]

    return diseases


@router.get("/crops", response_model=List[str])
async def get_supported_crops():
    """Get list of supported crops for disease detection."""
    return disease_service.SUPPORTED_CROPS
