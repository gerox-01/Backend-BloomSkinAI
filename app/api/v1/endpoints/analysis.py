"""
Skin analysis endpoints using Haut.ai integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.v1.schemas.analysis import (
    AnalysisUploadRequest,
    AnalysisUploadResponse,
    AnalysisResultsResponse
)
from app.infrastructure.services.haut_ai_service import HautAIService, get_haut_ai_service
from app.infrastructure.auth.firebase import get_current_user_firebase_uid


router = APIRouter()


@router.post("/upload", response_model=AnalysisUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_analysis_image(
    request: AnalysisUploadRequest,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    haut_service: HautAIService = Depends(get_haut_ai_service)
):
    """
    Upload image for skin analysis.

    This endpoint will:
    1. Create a subject in Haut.ai (using Firebase UID)
    2. Create a batch for the image
    3. Upload the image for analysis

    Returns the IDs needed to retrieve results later.
    """
    try:
        result = await haut_service.analyze_image(
            firebase_uid=firebase_uid,
            image_base64=request.image_base64,
            side_id=request.side_id,
            light_id=request.light_id
        )
        return AnalysisUploadResponse(**result)

    except Exception as e:
        logger.error(f"Error uploading image for analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image for analysis: {str(e)}"
        )


@router.get("/results/{image_id}", response_model=AnalysisResultsResponse)
async def get_analysis_results(
    image_id: str,
    subject_id: str,
    batch_id: str,
    firebase_uid: str = Depends(get_current_user_firebase_uid),
    haut_service: HautAIService = Depends(get_haut_ai_service)
):
    """
    Get analysis results for a specific image.

    Required query parameters:
    - subject_id: The subject ID from Haut.ai
    - batch_id: The batch ID from Haut.ai

    These IDs are returned when you upload an image.
    """
    try:
        results = await haut_service.get_results(
            subject_id=subject_id,
            batch_id=batch_id,
            image_id=image_id
        )

        return AnalysisResultsResponse(
            subject_id=subject_id,
            batch_id=batch_id,
            image_id=image_id,
            results=results
        )

    except ValueError as e:
        logger.error(f"Invalid response format from Haut.ai: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid response from analysis service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis results: {str(e)}"
        )
