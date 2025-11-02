"""
Product domain entities for personalized skincare product bundles.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ProductCategory(str, Enum):
    """Product category."""
    CLEANSER = "cleanser"
    TONER = "toner"
    MOISTURIZER = "moisturizer"
    SERUM = "serum"
    SUNSCREEN = "sunscreen"
    TREATMENT = "treatment"
    MASK = "mask"
    EXFOLIATOR = "exfoliator"
    EYE_CREAM = "eye_cream"
    SPOT_TREATMENT = "spot_treatment"


class PriceRange(str, Enum):
    """Price range category."""
    BUDGET = "budget"  # < $20
    MID_RANGE = "mid_range"  # $20-50
    PREMIUM = "premium"  # $50-100
    LUXURY = "luxury"  # > $100


@dataclass
class Product:
    """
    Individual skincare product.

    Can be part of a bundle or standalone recommendation.
    """

    name: str
    brand: str
    category: ProductCategory
    price: float
    currency: str = "USD"

    id: Optional[int] = None
    description: Optional[str] = None
    ingredients: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    product_url: Optional[str] = None  # Affiliate link or product page

    # Categorization
    price_range: Optional[PriceRange] = None
    skin_types: List[str] = field(default_factory=list)  # Suitable for skin types
    targets_concerns: List[str] = field(default_factory=list)  # What it treats

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Analytics
    recommendation_count: int = 0
    click_count: int = 0

    def increment_recommendations(self) -> None:
        """Increment recommendation counter."""
        self.recommendation_count += 1
        self.updated_at = datetime.utcnow()

    def increment_clicks(self) -> None:
        """Increment click counter."""
        self.click_count += 1
        self.updated_at = datetime.utcnow()

    def is_suitable_for_skin_type(self, skin_type: str) -> bool:
        """Check if product is suitable for given skin type."""
        if not self.skin_types:
            return True  # Suitable for all if not specified
        return skin_type in self.skin_types

    def targets_concern(self, concern: str) -> bool:
        """Check if product targets a specific concern."""
        return concern in self.targets_concerns


@dataclass
class ProductBundle:
    """
    Personalized product bundle recommendation.

    Generated based on user's skin analysis and profile.
    """

    user_id: int
    title: str
    description: str
    products: List[Product] = field(default_factory=list)

    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Generation context
    generated_from_analysis_id: Optional[str] = None
    skin_concerns_addressed: List[str] = field(default_factory=list)

    # Bundle metadata
    total_price: float = 0.0
    currency: str = "USD"
    estimated_duration_days: int = 30  # How long products last

    # User interaction
    is_active: bool = True
    is_purchased: bool = False
    purchased_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None

    def add_product(self, product: Product) -> None:
        """Add a product to the bundle."""
        self.products.append(product)
        self.recalculate_total()
        self.updated_at = datetime.utcnow()

    def remove_product(self, product_id: int) -> bool:
        """Remove a product from the bundle."""
        initial_length = len(self.products)
        self.products = [p for p in self.products if p.id != product_id]

        if len(self.products) < initial_length:
            self.recalculate_total()
            self.updated_at = datetime.utcnow()
            return True
        return False

    def recalculate_total(self) -> None:
        """Recalculate total price of bundle."""
        self.total_price = sum(p.price for p in self.products)

    def mark_viewed(self) -> None:
        """Mark bundle as viewed by user."""
        if not self.viewed_at:
            self.viewed_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def mark_purchased(self) -> None:
        """Mark bundle as purchased."""
        self.is_purchased = True
        self.purchased_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Increment recommendation count for all products
        for product in self.products:
            product.increment_recommendations()

    def get_products_by_category(self, category: ProductCategory) -> List[Product]:
        """Get all products in bundle of specific category."""
        return [p for p in self.products if p.category == category]

    def has_category(self, category: ProductCategory) -> bool:
        """Check if bundle contains product of specific category."""
        return any(p.category == category for p in self.products)

    def get_daily_cost(self) -> float:
        """Calculate daily cost based on duration."""
        if self.estimated_duration_days == 0:
            return 0.0
        return self.total_price / self.estimated_duration_days
