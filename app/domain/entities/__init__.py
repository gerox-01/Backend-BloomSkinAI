"""Domain entities for BloomSkin."""
from app.domain.entities.user import (
    User,
    AccountState,
    SkinType,
    Gender,
    SkinCareExperience,
    BudgetPreference,
    SkinGoal,
)
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
from app.domain.entities.subscription import (
    Subscription,
    SubscriptionPlatform,
    SubscriptionStatus,
    BillingPeriod,
)
from app.domain.entities.routine import (
    Routine,
    RoutineStep,
    RoutineTimeOfDay,
    RoutineFrequency,
)
from app.domain.entities.product import (
    Product,
    ProductBundle,
    ProductCategory,
    PriceRange,
)

__all__ = [
    # User
    "User",
    "AccountState",
    "SkinType",
    "Gender",
    "SkinCareExperience",
    "BudgetPreference",
    "SkinGoal",
    # Skin Analysis
    "SkinAnalysis",
    "AnalysisStatus",
    "SkinSeverity",
    "ImageQuality",
    "AcneByRegion",
    "AcneByType",
    "AcneAnalysisResults",
    "StructuredFeedback",
    # Subscription
    "Subscription",
    "SubscriptionPlatform",
    "SubscriptionStatus",
    "BillingPeriod",
    # Routine
    "Routine",
    "RoutineStep",
    "RoutineTimeOfDay",
    "RoutineFrequency",
    # Product
    "Product",
    "ProductBundle",
    "ProductCategory",
    "PriceRange",
]
