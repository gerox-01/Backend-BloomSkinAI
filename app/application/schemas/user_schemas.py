"""
Pydantic schemas for User API.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.user import (
    AccountState,
    SkinType,
    Gender,
    SkinCareExperience,
    BudgetPreference,
)


class SkinGoalSchema(BaseModel):
    """Skin goal schema."""

    id: str
    title: str
    color: str
    progress: float = Field(ge=0.0, le=1.0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBaseSchema(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    display_name: str
    name: str
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[Gender] = None


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a new user."""

    firebase_uid: str


class UserUpdateSchema(BaseModel):
    """Schema for updating a user."""

    display_name: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[Gender] = None
    skin_type: Optional[SkinType] = None
    skin_care_experience: Optional[SkinCareExperience] = None
    budget_preference: Optional[BudgetPreference] = None
    main_skin_concerns: Optional[List[str]] = None


class OnboardingUpdateSchema(BaseModel):
    """Schema for updating onboarding progress."""

    onboarding_step: int = Field(ge=0)
    face_image_captured: Optional[bool] = None
    face_analysis_completed: Optional[bool] = None


class SkinProfileUpdateSchema(BaseModel):
    """Schema for updating skin profile."""

    skin_type: Optional[SkinType] = None
    skin_care_experience: Optional[SkinCareExperience] = None
    budget_preference: Optional[BudgetPreference] = None
    main_skin_concerns: Optional[List[str]] = None


class UserResponseSchema(UserBaseSchema):
    """Schema for user response."""

    id: int
    firebase_uid: str
    account_state: AccountState
    created_at: datetime
    updated_at: datetime

    # Onboarding
    onboarding_completed: bool
    onboarding_step: int
    face_image_captured: bool
    face_analysis_completed: bool
    subscription_completed: bool

    # Skin Profile
    skin_type: Optional[SkinType] = None
    skin_care_experience: Optional[SkinCareExperience] = None
    budget_preference: Optional[BudgetPreference] = None
    main_skin_concerns: List[str] = []

    # Goals
    skin_goals: List[SkinGoalSchema] = []

    class Config:
        from_attributes = True


class UserListResponseSchema(BaseModel):
    """Schema for user list response."""

    total: int
    skip: int
    limit: int
    users: List[UserResponseSchema]
