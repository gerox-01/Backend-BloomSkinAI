"""
User domain entity for BloomSkin - Skincare SaaS platform.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class AccountState(str, Enum):
    """User account subscription state."""
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    TRIAL = "TRIAL"


class SkinType(str, Enum):
    """Skin type classification."""
    NORMAL = "Normal"
    OILY = "Oily"
    DRY = "Dry"
    COMBINATION = "Combination"
    SENSITIVE = "Sensitive"


class Gender(str, Enum):
    """User gender."""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "PreferNotToSay"


class SkinCareExperience(str, Enum):
    """User's skincare experience level."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class BudgetPreference(str, Enum):
    """User's budget preference for skincare products."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    LUXURY = "Luxury"

@dataclass
class SkinGoal:
    """Represents a user's skin goal with progress tracking."""
    id: str
    title: str
    color: str
    progress: float  # 0.0 to 1.0
    created_at: datetime
    updated_at: datetime

    def update_progress(self, new_progress: float) -> None:
        """Update goal progress (0-1 range)."""
        self.progress = max(0.0, min(1.0, new_progress))
        self.updated_at = datetime.utcnow()


@dataclass
class User:
    """
    User domain entity for BloomSkin platform.

    Represents a user with complete skincare profile and preferences.
    """

    # Firebase Auth (readonly)
    firebase_uid: str  # Firebase UID from authentication
    email: str

    # Basic Profile
    display_name: str
    name: str
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[Gender] = None

    # Account State
    id: Optional[int] = None
    account_state: AccountState = AccountState.FREE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Onboarding Progress
    onboarding_completed: bool = False
    onboarding_step: int = 0
    face_image_captured: bool = False
    face_analysis_completed: bool = False
    subscription_completed: bool = False

    # Skin Profile
    skin_type: Optional[SkinType] = None
    skin_care_experience: Optional[SkinCareExperience] = None
    budget_preference: Optional[BudgetPreference] = None
    main_skin_concerns: List[str] = field(default_factory=list)  # e.g., ["Dark Spots", "Sensitivity"]

    # Goals & Progress
    skin_goals: List[SkinGoal] = field(default_factory=list)

    def is_premium(self) -> bool:
        """Check if user has premium account."""
        return self.account_state == AccountState.PREMIUM

    def is_free(self) -> bool:
        """Check if user has free account."""
        return self.account_state == AccountState.FREE

    def is_trial(self) -> bool:
        """Check if user is on trial."""
        return self.account_state == AccountState.TRIAL

    def upgrade_to_premium(self) -> None:
        """Upgrade user to premium account."""
        self.account_state = AccountState.PREMIUM
        self.updated_at = datetime.utcnow()

    def downgrade_to_free(self) -> None:
        """Downgrade user to free account."""
        self.account_state = AccountState.FREE
        self.updated_at = datetime.utcnow()

    def start_trial(self) -> None:
        """Start trial period."""
        self.account_state = AccountState.TRIAL
        self.updated_at = datetime.utcnow()

    def complete_onboarding_step(self, step: int) -> None:
        """Mark an onboarding step as complete."""
        self.onboarding_step = max(self.onboarding_step, step)
        self.updated_at = datetime.utcnow()

        # Check if onboarding is fully complete
        if self.onboarding_step >= 11:  # Based on your data showing step 11
            self.onboarding_completed = True

    def update_skin_profile(
        self,
        skin_type: Optional[SkinType] = None,
        experience: Optional[SkinCareExperience] = None,
        budget: Optional[BudgetPreference] = None,
        concerns: Optional[List[str]] = None,
    ) -> None:
        """Update user's skin profile."""
        if skin_type:
            self.skin_type = skin_type
        if experience:
            self.skin_care_experience = experience
        if budget:
            self.budget_preference = budget
        if concerns is not None:
            self.main_skin_concerns = concerns
        self.updated_at = datetime.utcnow()

    def add_skin_goal(self, goal: SkinGoal) -> None:
        """Add a new skin goal."""
        self.skin_goals.append(goal)
        self.updated_at = datetime.utcnow()

    def update_goal_progress(self, goal_id: str, progress: float) -> None:
        """Update progress for a specific goal."""
        for goal in self.skin_goals:
            if goal.id == goal_id:
                goal.update_progress(progress)
                self.updated_at = datetime.utcnow()
                break
