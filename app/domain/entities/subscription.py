"""
Subscription domain entity for handling user subscriptions (Apple/Google In-App).
"""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum


class SubscriptionPlatform(str, Enum):
    """Platform where subscription was purchased."""
    APPLE = "apple"
    GOOGLE = "google"
    STRIPE = "stripe"  # Future support
    WEB = "web"  # Future support


class SubscriptionStatus(str, Enum):
    """Status of the subscription."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    GRACE_PERIOD = "grace_period"  # Renewal failed but still active
    ON_HOLD = "on_hold"  # Payment issue


class BillingPeriod(str, Enum):
    """Billing period for subscription."""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


@dataclass
class Subscription:
    """
    Subscription domain entity.

    Handles user subscriptions from Apple/Google In-App Purchases.
    """

    user_id: int
    platform: SubscriptionPlatform
    plan_name: str
    product_id: str  # e.g., "com.bloom.bloomskinai.monthly"
    billing_period: BillingPeriod
    price: float
    currency: str = "USD"

    # Subscription state
    id: Optional[int] = None
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    is_active: bool = False

    # External platform data
    platform_subscription_id: str = ""  # Apple/Google transaction ID
    original_transaction_id: Optional[str] = None  # For renewals
    purchase_token: Optional[str] = None  # Google Play token

    # Dates
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Trial
    is_trial: bool = False
    trial_end_date: Optional[datetime] = None

    # Auto-renewal
    auto_renew_enabled: bool = True

    def activate(self, expires_at: datetime, next_billing: datetime) -> None:
        """Activate the subscription."""
        self.status = SubscriptionStatus.ACTIVE
        self.is_active = True
        self.activated_at = datetime.utcnow()
        self.expires_at = expires_at
        self.next_billing_date = next_billing
        self.updated_at = datetime.utcnow()

    def renew(self, new_expires_at: datetime, new_next_billing: datetime) -> None:
        """Renew the subscription."""
        self.expires_at = new_expires_at
        self.next_billing_date = new_next_billing
        self.status = SubscriptionStatus.ACTIVE
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def cancel(self, immediate: bool = False) -> None:
        """
        Cancel the subscription.

        Args:
            immediate: If True, cancel immediately. If False, mark for cancellation
                      at end of billing period.
        """
        self.cancelled_at = datetime.utcnow()
        self.auto_renew_enabled = False
        self.updated_at = datetime.utcnow()

        if immediate:
            self.status = SubscriptionStatus.CANCELLED
            self.is_active = False
            self.expires_at = datetime.utcnow()

    def expire(self) -> None:
        """Mark subscription as expired."""
        self.status = SubscriptionStatus.EXPIRED
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def put_on_hold(self) -> None:
        """Put subscription on hold (payment issue)."""
        self.status = SubscriptionStatus.ON_HOLD
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def enter_grace_period(self) -> None:
        """Enter grace period (renewal failed but still active)."""
        self.status = SubscriptionStatus.GRACE_PERIOD
        self.is_active = True  # Still active during grace
        self.updated_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if subscription has expired."""
        if not self.expires_at:
            return True
        return datetime.utcnow() > self.expires_at

    def days_until_expiry(self) -> int:
        """Get number of days until expiry."""
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def is_renewable(self) -> bool:
        """Check if subscription can be renewed."""
        return self.auto_renew_enabled and not self.is_expired()

    def start_trial(self, trial_days: int = 7) -> None:
        """Start trial period."""
        self.is_trial = True
        self.trial_end_date = datetime.utcnow() + timedelta(days=trial_days)
        self.expires_at = self.trial_end_date
        self.status = SubscriptionStatus.ACTIVE
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def get_billing_period_days(self) -> int:
        """Get number of days in billing period."""
        period_map = {
            BillingPeriod.WEEKLY: 7,
            BillingPeriod.MONTHLY: 30,
            BillingPeriod.YEARLY: 365,
        }
        return period_map.get(self.billing_period, 30)
