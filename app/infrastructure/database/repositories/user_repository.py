"""
User Repository implementation - Data access layer for users.
"""
from typing import List, Optional
from datetime import datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import UserRepository
from app.domain.entities.user import User, AccountState, SkinType, Gender, SkinCareExperience, BudgetPreference, SkinGoal
from app.infrastructure.database.models import UserModel
from app.core.logging import logger


class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of User Repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        # Convert skin goals from JSON
        skin_goals = []
        if model.skin_goals:
            for goal_data in model.skin_goals:
                skin_goals.append(
                    SkinGoal(
                        id=goal_data["id"],
                        title=goal_data["title"],
                        color=goal_data["color"],
                        progress=goal_data["progress"],
                        created_at=datetime.fromisoformat(goal_data["created_at"]),
                        updated_at=datetime.fromisoformat(goal_data["updated_at"]),
                    )
                )

        return User(
            id=model.id,
            firebase_uid=model.firebase_uid,
            email=model.email,
            display_name=model.display_name,
            name=model.name,
            bio=model.bio,
            profile_photo_url=model.profile_photo_url,
            date_of_birth=model.date_of_birth,
            gender=model.gender,
            account_state=model.account_state,
            created_at=model.created_at,
            updated_at=model.updated_at,
            onboarding_completed=model.onboarding_completed,
            onboarding_step=model.onboarding_step,
            face_image_captured=model.face_image_captured,
            face_analysis_completed=model.face_analysis_completed,
            subscription_completed=model.subscription_completed,
            skin_type=model.skin_type,
            skin_care_experience=model.skin_care_experience,
            budget_preference=model.budget_preference,
            main_skin_concerns=model.main_skin_concerns or [],
            skin_goals=skin_goals,
        )

    def _entity_to_model(self, entity: User, model: Optional[UserModel] = None) -> UserModel:
        """Convert domain entity to ORM model."""
        if model is None:
            model = UserModel()

        # Convert skin goals to JSON
        skin_goals_json = [
            {
                "id": goal.id,
                "title": goal.title,
                "color": goal.color,
                "progress": goal.progress,
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat(),
            }
            for goal in entity.skin_goals
        ]

        # Update model fields
        model.firebase_uid = entity.firebase_uid
        model.email = entity.email
        model.display_name = entity.display_name
        model.name = entity.name
        model.bio = entity.bio
        model.profile_photo_url = entity.profile_photo_url
        model.date_of_birth = entity.date_of_birth
        model.gender = entity.gender
        model.account_state = entity.account_state
        model.onboarding_completed = entity.onboarding_completed
        model.onboarding_step = entity.onboarding_step
        model.face_image_captured = entity.face_image_captured
        model.face_analysis_completed = entity.face_analysis_completed
        model.subscription_completed = entity.subscription_completed
        model.skin_type = entity.skin_type
        model.skin_care_experience = entity.skin_care_experience
        model.budget_preference = entity.budget_preference
        model.main_skin_concerns = entity.main_skin_concerns
        model.skin_goals = skin_goals_json

        return model

    async def create(self, entity: User) -> User:
        """Create a new user."""
        try:
            model = self._entity_to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            logger.info(f"Created user: {model.id} ({model.firebase_uid})")
            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_by_id(self, entity_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.id == entity_id)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error(f"Error fetching user by ID {entity_id}: {e}")
            raise

    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID."""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.firebase_uid == firebase_uid)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error(f"Error fetching user by Firebase UID {firebase_uid}: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        try:
            result = await self.session.execute(
                select(UserModel).offset(skip).limit(limit)
            )
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            raise

    async def update(self, entity_id: int, entity: User) -> Optional[User]:
        """Update an existing user."""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.id == entity_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            # Update model from entity
            model = self._entity_to_model(entity, model)
            model.updated_at = datetime.utcnow()

            await self.session.flush()
            await self.session.refresh(model)

            logger.info(f"Updated user: {model.id}")
            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"Error updating user {entity_id}: {e}")
            raise

    async def delete(self, entity_id: int) -> bool:
        """Delete a user."""
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.id == entity_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            await self.session.delete(model)
            await self.session.flush()

            logger.info(f"Deleted user: {entity_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user {entity_id}: {e}")
            raise

    async def get_premium_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all premium users."""
        try:
            result = await self.session.execute(
                select(UserModel)
                .where(UserModel.account_state == AccountState.PREMIUM)
                .offset(skip)
                .limit(limit)
            )
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

        except Exception as e:
            logger.error(f"Error fetching premium users: {e}")
            raise

    async def get_users_by_skin_type(self, skin_type: SkinType, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by skin type."""
        try:
            result = await self.session.execute(
                select(UserModel)
                .where(UserModel.skin_type == skin_type)
                .offset(skip)
                .limit(limit)
            )
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

        except Exception as e:
            logger.error(f"Error fetching users by skin type: {e}")
            raise
