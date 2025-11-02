"""
Skin Analysis domain entity for AI-powered acne and skin analysis.
"""
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum


class AnalysisStatus(str, Enum):
    """Status of analysis processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class SkinSeverity(str, Enum):
    """Acne severity classification."""
    CLEAR = "clear"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ImageQuality(str, Enum):
    """Quality assessment of submitted image."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AcneByRegion:
    """Acne count by facial region."""
    forehead: int = 0
    cheeks: int = 0
    nose: int = 0
    chin: int = 0


@dataclass
class AcneByType:
    """Acne count by type."""
    blackheads: int = 0
    whiteheads: int = 0
    papules: int = 0
    pustules: int = 0
    nodules: int = 0
    cysts: int = 0


@dataclass
class AcneAnalysisResults:
    """Detailed acne analysis results."""
    by_region: AcneByRegion
    by_type: AcneByType
    severity: SkinSeverity
    total_lesions: int
    analyzed_at: datetime

    def get_severity_score(self) -> int:
        """Get numerical severity score (0-100)."""
        severity_map = {
            SkinSeverity.CLEAR: 0,
            SkinSeverity.MILD: 25,
            SkinSeverity.MODERATE: 50,
            SkinSeverity.SEVERE: 75,
        }
        return severity_map.get(self.severity, 0)


@dataclass
class StructuredFeedback:
    """AI-generated structured feedback for user."""
    main_summary: str
    motivation: str
    severity_data: str
    skin_insights: List[str]
    tips: List[str]


@dataclass
class SkinAnalysis:
    """
    Skin Analysis domain entity.

    Represents an AI-powered analysis of a user's skin photo.
    """

    user_id: int
    image_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Analysis state
    id: Optional[str] = None  # UUID
    status: AnalysisStatus = AnalysisStatus.PENDING
    image_quality: Optional[ImageQuality] = None
    analysis_complete: bool = False

    # Analysis results (populated after AI processing)
    acne_analysis: Optional[AcneAnalysisResults] = None
    structured_feedback: Optional[StructuredFeedback] = None

    # Raw AI response (optional, for debugging/audit)
    raw_metadata: Optional[Dict] = None

    def mark_processing(self) -> None:
        """Mark analysis as currently processing."""
        self.status = AnalysisStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(
        self,
        acne_analysis: AcneAnalysisResults,
        feedback: StructuredFeedback,
        image_quality: ImageQuality,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Mark analysis as completed with results."""
        self.status = AnalysisStatus.ANALYZED
        self.analysis_complete = True
        self.acne_analysis = acne_analysis
        self.structured_feedback = feedback
        self.image_quality = image_quality
        self.raw_metadata = metadata
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Mark analysis as failed."""
        self.status = AnalysisStatus.FAILED
        self.updated_at = datetime.utcnow()

    def is_clear_skin(self) -> bool:
        """Check if analysis shows clear skin."""
        if not self.acne_analysis:
            return False
        return self.acne_analysis.total_lesions == 0

    def get_main_concern_area(self) -> Optional[str]:
        """Get the facial region with most acne."""
        if not self.acne_analysis:
            return None

        regions = self.acne_analysis.by_region
        region_counts = {
            "forehead": regions.forehead,
            "cheeks": regions.cheeks,
            "nose": regions.nose,
            "chin": regions.chin,
        }

        if max(region_counts.values()) == 0:
            return None

        return max(region_counts, key=region_counts.get)  # type: ignore

    def get_dominant_acne_type(self) -> Optional[str]:
        """Get the most common type of acne."""
        if not self.acne_analysis:
            return None

        types = self.acne_analysis.by_type
        type_counts = {
            "blackheads": types.blackheads,
            "whiteheads": types.whiteheads,
            "papules": types.papules,
            "pustules": types.pustules,
            "nodules": types.nodules,
            "cysts": types.cysts,
        }

        if max(type_counts.values()) == 0:
            return None

        return max(type_counts, key=type_counts.get)  # type: ignore
