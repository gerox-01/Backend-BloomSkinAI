"""
Skin Analysis Repository implementation.
"""
from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.skin_analysis import (
    SkinAnalysis,
    AnalysisStatus,
    SkinSeverity,
    ImageQuality,
    AcneByRegion,
    AcneByType,
    AcneAnalysisResults,
    StructuredFeedback,
)
from app.infrastructure.database.models import SkinAnalysisModel
from app.core.logging import logger


class PostgresSkinAnalysisRepository:
    """PostgreSQL implementation of Skin Analysis Repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: SkinAnalysisModel) -> SkinAnalysis:
        """Convert ORM model to domain entity."""
        # Parse analysis results
        acne_analysis = None
        if model.acne_analysis_results:
            data = model.acne_analysis_results
            acne_analysis = AcneAnalysisResults(
                by_region=AcneByRegion(**data["by_region"]),
                by_type=AcneByType(**data["by_type"]),
                severity=SkinSeverity(data["severity"]),
                total_lesions=data["total_lesions"],
                analyzed_at=datetime.fromisoformat(data["analyzed_at"]),
            )

        # Parse feedback
        feedback = None
        if model.structured_feedback:
            feedback = StructuredFeedback(**model.structured_feedback)

        return SkinAnalysis(
            id=model.id,
            user_id=model.user_id,
            image_url=model.image_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=model.status,
            image_quality=model.image_quality,
            analysis_complete=model.analysis_complete,
            acne_analysis=acne_analysis,
            structured_feedback=feedback,
            raw_metadata=model.raw_metadata,
        )

    def _entity_to_model(self, entity: SkinAnalysis, model: Optional[SkinAnalysisModel] = None) -> SkinAnalysisModel:
        """Convert domain entity to ORM model."""
        if model is None:
            model = SkinAnalysisModel()
            model.id = entity.id or str(uuid.uuid4())

        # Convert analysis results to JSON
        acne_analysis_json = None
        if entity.acne_analysis:
            acne_analysis_json = {
                "by_region": {
                    "forehead": entity.acne_analysis.by_region.forehead,
                    "cheeks": entity.acne_analysis.by_region.cheeks,
                    "nose": entity.acne_analysis.by_region.nose,
                    "chin": entity.acne_analysis.by_region.chin,
                },
                "by_type": {
                    "blackheads": entity.acne_analysis.by_type.blackheads,
                    "whiteheads": entity.acne_analysis.by_type.whiteheads,
                    "papules": entity.acne_analysis.by_type.papules,
                    "pustules": entity.acne_analysis.by_type.pustules,
                    "nodules": entity.acne_analysis.by_type.nodules,
                    "cysts": entity.acne_analysis.by_type.cysts,
                },
                "severity": entity.acne_analysis.severity.value,
                "total_lesions": entity.acne_analysis.total_lesions,
                "analyzed_at": entity.acne_analysis.analyzed_at.isoformat(),
            }

        # Convert feedback to JSON
        feedback_json = None
        if entity.structured_feedback:
            feedback_json = {
                "main_summary": entity.structured_feedback.main_summary,
                "motivation": entity.structured_feedback.motivation,
                "severity_data": entity.structured_feedback.severity_data,
                "skin_insights": entity.structured_feedback.skin_insights,
                "tips": entity.structured_feedback.tips,
            }

        model.user_id = entity.user_id
        model.image_url = entity.image_url
        model.status = entity.status
        model.image_quality = entity.image_quality
        model.analysis_complete = entity.analysis_complete
        model.acne_analysis_results = acne_analysis_json
        model.structured_feedback = feedback_json
        model.raw_metadata = entity.raw_metadata

        return model

    async def create(self, entity: SkinAnalysis) -> SkinAnalysis:
        """Create a new skin analysis."""
        try:
            model = self._entity_to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            logger.info(f"Created skin analysis: {model.id} for user: {model.user_id}")
            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"Error creating skin analysis: {e}")
            raise

    async def get_by_id(self, analysis_id: str) -> Optional[SkinAnalysis]:
        """Get skin analysis by ID."""
        try:
            result = await self.session.execute(
                select(SkinAnalysisModel).where(SkinAnalysisModel.id == analysis_id)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error(f"Error fetching skin analysis {analysis_id}: {e}")
            raise

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SkinAnalysis]:
        """Get all skin analyses for a user."""
        try:
            result = await self.session.execute(
                select(SkinAnalysisModel)
                .where(SkinAnalysisModel.user_id == user_id)
                .order_by(desc(SkinAnalysisModel.created_at))
                .offset(skip)
                .limit(limit)
            )
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

        except Exception as e:
            logger.error(f"Error fetching skin analyses for user {user_id}: {e}")
            raise

    async def get_latest_analysis(self, user_id: int) -> Optional[SkinAnalysis]:
        """Get the most recent skin analysis for a user."""
        try:
            result = await self.session.execute(
                select(SkinAnalysisModel)
                .where(SkinAnalysisModel.user_id == user_id)
                .where(SkinAnalysisModel.analysis_complete == True)
                .order_by(desc(SkinAnalysisModel.created_at))
                .limit(1)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error(f"Error fetching latest analysis for user {user_id}: {e}")
            raise

    async def update(self, analysis_id: str, entity: SkinAnalysis) -> Optional[SkinAnalysis]:
        """Update an existing skin analysis."""
        try:
            result = await self.session.execute(
                select(SkinAnalysisModel).where(SkinAnalysisModel.id == analysis_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            model = self._entity_to_model(entity, model)
            model.updated_at = datetime.utcnow()

            await self.session.flush()
            await self.session.refresh(model)

            logger.info(f"Updated skin analysis: {analysis_id}")
            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"Error updating skin analysis {analysis_id}: {e}")
            raise

    async def delete(self, analysis_id: str) -> bool:
        """Delete a skin analysis."""
        try:
            result = await self.session.execute(
                select(SkinAnalysisModel).where(SkinAnalysisModel.id == analysis_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            await self.session.delete(model)
            await self.session.flush()

            logger.info(f"Deleted skin analysis: {analysis_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting skin analysis {analysis_id}: {e}")
            raise
