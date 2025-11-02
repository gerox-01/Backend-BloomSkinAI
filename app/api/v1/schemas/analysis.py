"""
Schemas for skin analysis endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union


class AnalysisUploadRequest(BaseModel):
    """Schema for uploading image for analysis."""

    image_base64: str = Field(..., description="Base64 encoded image")
    side_id: int = Field(default=1, description="Side ID (1 for front)")
    light_id: int = Field(default=1, description="Light ID (1 for standard)")


class AnalysisUploadResponse(BaseModel):
    """Schema for analysis upload response."""

    subject_id: str = Field(..., description="Haut.ai subject ID")
    batch_id: str = Field(..., description="Haut.ai batch ID")
    image_id: str = Field(..., description="Haut.ai image ID")
    message: str = Field(..., description="Status message")


class AnalysisResultsResponse(BaseModel):
    """Schema for analysis results response."""

    subject_id: str
    batch_id: str
    image_id: str
    results: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="Analysis results from Haut.ai - can be array or object")
