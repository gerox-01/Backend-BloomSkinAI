"""
SQLAlchemy ORM models for BloomSkin - Infrastructure layer.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Float,
    Enum as SQLEnum,
    ForeignKey,
    JSON,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base
from app.domain.entities.user import (
    AccountState,
    SkinType,
    Gender,
    SkinCareExperience,
    BudgetPreference,
)
from app.domain.entities.skin_analysis import AnalysisStatus, SkinSeverity, ImageQuality
from app.domain.entities.subscription import (
    SubscriptionPlatform,
    SubscriptionStatus,
    BillingPeriod,
)
from app.domain.entities.routine import RoutineTimeOfDay, RoutineFrequency
from app.domain.entities.product import ProductCategory, PriceRange


class UserModel(Base):
    """User ORM model for BloomSkin users."""

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Firebase Auth
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Basic Profile
    display_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    profile_photo_url = Column(String(512), nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    gender = Column(SQLEnum(Gender, name="gender"), nullable=True)

    # Account State
    account_state = Column(
        SQLEnum(AccountState, name="account_state"),
        default=AccountState.FREE,
        nullable=False,
        index=True,
    )

    # Onboarding Progress
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_step = Column(Integer, default=0, nullable=False)
    face_image_captured = Column(Boolean, default=False, nullable=False)
    face_analysis_completed = Column(Boolean, default=False, nullable=False)
    subscription_completed = Column(Boolean, default=False, nullable=False)

    # Skin Profile
    skin_type = Column(SQLEnum(SkinType, name="skin_type"), nullable=True)
    skin_care_experience = Column(
        SQLEnum(SkinCareExperience, name="skin_care_experience"), nullable=True
    )
    budget_preference = Column(
        SQLEnum(BudgetPreference, name="budget_preference"), nullable=True
    )
    main_skin_concerns = Column(JSON, nullable=True)  # List[str]

    # Skin Goals (stored as JSON array)
    skin_goals = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    skin_analyses = relationship("SkinAnalysisModel", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("SubscriptionModel", back_populates="user", cascade="all, delete-orphan")
    routines = relationship("RoutineModel", back_populates="user", cascade="all, delete-orphan")
    product_bundles = relationship("ProductBundleModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, firebase_uid={self.firebase_uid})>"


class SkinAnalysisModel(Base):
    """Skin Analysis ORM model."""

    __tablename__ = "skin_analyses"

    # Primary Key (UUID as string)
    id = Column(String(36), primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Image
    image_url = Column(String(512), nullable=False)
    image_quality = Column(SQLEnum(ImageQuality, name="image_quality"), nullable=True)

    # Status
    status = Column(
        SQLEnum(AnalysisStatus, name="analysis_status"),
        default=AnalysisStatus.PENDING,
        nullable=False,
        index=True,
    )
    analysis_complete = Column(Boolean, default=False, nullable=False)

    # Analysis Results (stored as JSON)
    acne_analysis_results = Column(JSON, nullable=True)
    structured_feedback = Column(JSON, nullable=True)
    raw_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("UserModel", back_populates="skin_analyses")

    def __repr__(self) -> str:
        return f"<SkinAnalysis(id={self.id}, user_id={self.user_id}, status={self.status})>"


class SubscriptionModel(Base):
    """Subscription ORM model for Apple/Google In-App Purchases."""

    __tablename__ = "subscriptions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Platform & Product Info
    platform = Column(
        SQLEnum(SubscriptionPlatform, name="subscription_platform"),
        nullable=False,
        index=True,
    )
    plan_name = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False, index=True)
    billing_period = Column(
        SQLEnum(BillingPeriod, name="billing_period"), nullable=False
    )

    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Subscription State
    status = Column(
        SQLEnum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.PENDING,
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=False, nullable=False, index=True)

    # External Platform Data
    platform_subscription_id = Column(String(255), nullable=False, index=True)
    original_transaction_id = Column(String(255), nullable=True)
    purchase_token = Column(Text, nullable=True)

    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    activated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Trial
    is_trial = Column(Boolean, default=False, nullable=False)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)

    # Auto-renewal
    auto_renew_enabled = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"


class RoutineModel(Base):
    """Skincare Routine ORM model."""

    __tablename__ = "routines"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Routine Info
    title = Column(String(255), nullable=False)
    time_of_day = Column(
        SQLEnum(RoutineTimeOfDay, name="routine_time_of_day"), nullable=False
    )
    frequency = Column(SQLEnum(RoutineFrequency, name="routine_frequency"), nullable=False)

    # Steps (stored as JSON array)
    steps = Column(JSON, nullable=False, default=[])

    # State
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Reminders
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    reminder_time = Column(Time, nullable=True)

    # Tracking
    total_completions = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    last_completed_at = Column(DateTime(timezone=True), nullable=True)

    # AI Generation
    is_ai_generated = Column(Boolean, default=False, nullable=False)
    generated_from_analysis_id = Column(String(36), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("UserModel", back_populates="routines")

    def __repr__(self) -> str:
        return f"<Routine(id={self.id}, user_id={self.user_id}, title={self.title})>"


class ProductModel(Base):
    """Product ORM model."""

    __tablename__ = "products"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Product Info
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=False, index=True)
    category = Column(
        SQLEnum(ProductCategory, name="product_category"), nullable=False, index=True
    )
    description = Column(Text, nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    price_range = Column(SQLEnum(PriceRange, name="price_range"), nullable=True)

    # Product Details
    ingredients = Column(JSON, nullable=True)  # List[str]
    image_url = Column(String(512), nullable=True)
    product_url = Column(String(512), nullable=True)

    # Categorization
    skin_types = Column(JSON, nullable=True)  # List[str]
    targets_concerns = Column(JSON, nullable=True)  # List[str]

    # State
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Analytics
    recommendation_count = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, brand={self.brand})>"


class ProductBundleModel(Base):
    """Product Bundle ORM model."""

    __tablename__ = "product_bundles"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Bundle Info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Products (stored as JSON array of product IDs)
    product_ids = Column(JSON, nullable=False, default=[])

    # Generation Context
    generated_from_analysis_id = Column(String(36), nullable=True)
    skin_concerns_addressed = Column(JSON, nullable=True)  # List[str]

    # Bundle Metadata
    total_price = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    estimated_duration_days = Column(Integer, default=30, nullable=False)

    # User Interaction
    is_active = Column(Boolean, default=True, nullable=False)
    is_purchased = Column(Boolean, default=False, nullable=False)
    purchased_at = Column(DateTime(timezone=True), nullable=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("UserModel", back_populates="product_bundles")

    def __repr__(self) -> str:
        return f"<ProductBundle(id={self.id}, user_id={self.user_id}, title={self.title})>"
