"""
Firestore User Repository implementation.
"""
from typing import List, Optional
from datetime import datetime

from app.domain.entities.user import User, SkinGoal
from app.infrastructure.database.firestore_client import FirestoreClient
from app.core.logging import logger


class FirestoreUserRepository:
    """Firestore implementation of User Repository."""

    def __init__(self, client: FirestoreClient):
        self.client = client
        self.collection = client.get_collection('users')

    def _doc_to_entity(self, doc) -> Optional[User]:
        """Convert Firestore document to User entity."""
        if not doc.exists:
            return None

        data = doc.to_dict()
        doc_id = doc.id

        # Convert skin goals
        skin_goals = []
        if data.get('skin_goals'):
            for goal_data in data['skin_goals']:
                skin_goals.append(
                    SkinGoal(
                        id=goal_data['id'],
                        title=goal_data['title'],
                        color=goal_data['color'],
                        progress=goal_data['progress'],
                        created_at=goal_data['created_at'],
                        updated_at=goal_data['updated_at'],
                    )
                )

        return User(
            id=int(data.get('id', 0)),
            firebase_uid=data['firebase_uid'],
            email=data['email'],
            display_name=data['display_name'],
            name=data['name'],
            bio=data.get('bio'),
            profile_photo_url=data.get('profile_photo_url'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            account_state=data['account_state'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            onboarding_completed=data.get('onboarding_completed', False),
            onboarding_step=data.get('onboarding_step', 0),
            face_image_captured=data.get('face_image_captured', False),
            face_analysis_completed=data.get('face_analysis_completed', False),
            subscription_completed=data.get('subscription_completed', False),
            skin_type=data.get('skin_type'),
            skin_care_experience=data.get('skin_care_experience'),
            budget_preference=data.get('budget_preference'),
            main_skin_concerns=data.get('main_skin_concerns', []),
            skin_goals=skin_goals,
        )

    def _entity_to_dict(self, entity: User) -> dict:
        """Convert User entity to Firestore document dict."""
        # Convert skin goals to dict
        skin_goals_dict = [
            {
                'id': goal.id,
                'title': goal.title,
                'color': goal.color,
                'progress': goal.progress,
                'created_at': goal.created_at,
                'updated_at': goal.updated_at,
            }
            for goal in entity.skin_goals
        ]

        return {
            'id': entity.id or 0,
            'firebase_uid': entity.firebase_uid,
            'email': entity.email,
            'display_name': entity.display_name,
            'name': entity.name,
            'bio': entity.bio,
            'profile_photo_url': entity.profile_photo_url,
            'date_of_birth': entity.date_of_birth,
            'gender': entity.gender.value if entity.gender else None,
            'account_state': entity.account_state.value,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at,
            'onboarding_completed': entity.onboarding_completed,
            'onboarding_step': entity.onboarding_step,
            'face_image_captured': entity.face_image_captured,
            'face_analysis_completed': entity.face_analysis_completed,
            'subscription_completed': entity.subscription_completed,
            'skin_type': entity.skin_type.value if entity.skin_type else None,
            'skin_care_experience': entity.skin_care_experience.value if entity.skin_care_experience else None,
            'budget_preference': entity.budget_preference.value if entity.budget_preference else None,
            'main_skin_concerns': entity.main_skin_concerns,
            'skin_goals': skin_goals_dict,
        }

    async def create(self, entity: User) -> User:
        """Create a new user."""
        try:
            # Use firebase_uid as document ID
            doc_ref = self.collection.document(entity.firebase_uid)

            # Convert entity to dict
            user_data = self._entity_to_dict(entity)

            # Set the document
            doc_ref.set(user_data)

            logger.info(f"Created user: {entity.firebase_uid}")
            return entity

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID."""
        try:
            doc_ref = self.collection.document(firebase_uid)
            doc = doc_ref.get()

            return self._doc_to_entity(doc)

        except Exception as e:
            logger.error(f"Error fetching user by Firebase UID {firebase_uid}: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            query = self.collection.where('email', '==', email).limit(1)
            docs = query.stream()

            for doc in docs:
                return self._doc_to_entity(doc)

            return None

        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        try:
            query = self.collection.offset(skip).limit(limit)
            docs = query.stream()

            users = []
            for doc in docs:
                user = self._doc_to_entity(doc)
                if user:
                    users.append(user)

            return users

        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            raise

    async def update(self, firebase_uid: str, entity: User) -> Optional[User]:
        """Update an existing user."""
        try:
            doc_ref = self.collection.document(firebase_uid)

            # Update timestamp
            entity.updated_at = datetime.utcnow()

            # Convert to dict and update
            user_data = self._entity_to_dict(entity)
            doc_ref.update(user_data)

            logger.info(f"Updated user: {firebase_uid}")
            return entity

        except Exception as e:
            logger.error(f"Error updating user {firebase_uid}: {e}")
            raise

    async def delete(self, firebase_uid: str) -> bool:
        """Delete a user."""
        try:
            doc_ref = self.collection.document(firebase_uid)
            doc_ref.delete()

            logger.info(f"Deleted user: {firebase_uid}")
            return True

        except Exception as e:
            logger.error(f"Error deleting user {firebase_uid}: {e}")
            raise

    async def get_premium_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all premium users."""
        try:
            query = (
                self.collection
                .where('account_state', '==', 'PREMIUM')
                .offset(skip)
                .limit(limit)
            )
            docs = query.stream()

            users = []
            for doc in docs:
                user = self._doc_to_entity(doc)
                if user:
                    users.append(user)

            return users

        except Exception as e:
            logger.error(f"Error fetching premium users: {e}")
            raise
