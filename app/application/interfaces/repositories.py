"""
Repository interfaces - Abstract base classes for data access.

Following the Repository pattern and Dependency Inversion Principle.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from app.domain.entities.user import User

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface with common CRUD operations."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def update(self, entity_id: int, entity: T) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        pass


class UserRepository(BaseRepository[User]):
    """User repository interface with user-specific operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        pass

    @abstractmethod
    async def verify_user(self, user_id: int) -> Optional[User]:
        """Verify user email."""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login timestamp."""
        pass
