"""
Skincare Routine domain entity for daily routines and reminders.
"""
from datetime import datetime, time
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class RoutineTimeOfDay(str, Enum):
    """Time of day for routine."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class RoutineFrequency(str, Enum):
    """How often the routine should be performed."""
    DAILY = "daily"
    TWICE_DAILY = "twice_daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


@dataclass
class RoutineStep:
    """Individual step in a skincare routine."""
    id: str
    order: int  # Step order (1, 2, 3, etc.)
    title: str
    description: str
    product_name: Optional[str] = None
    duration_seconds: Optional[int] = None  # How long to perform step
    is_completed_today: bool = False


@dataclass
class Routine:
    """
    Skincare Routine domain entity.

    Represents a personalized daily skincare routine for a user.
    """

    user_id: int
    title: str
    time_of_day: RoutineTimeOfDay
    frequency: RoutineFrequency
    steps: List[RoutineStep] = field(default_factory=list)

    # Routine state
    id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Reminders
    reminder_enabled: bool = True
    reminder_time: Optional[time] = None  # Specific time for reminder

    # Tracking
    total_completions: int = 0
    current_streak: int = 0  # Days in a row completed
    best_streak: int = 0
    last_completed_at: Optional[datetime] = None

    # AI-generated recommendations
    is_ai_generated: bool = False
    generated_from_analysis_id: Optional[str] = None  # Reference to SkinAnalysis

    def add_step(self, step: RoutineStep) -> None:
        """Add a new step to the routine."""
        self.steps.append(step)
        self.steps.sort(key=lambda s: s.order)
        self.updated_at = datetime.utcnow()

    def remove_step(self, step_id: str) -> bool:
        """Remove a step from the routine."""
        initial_length = len(self.steps)
        self.steps = [s for s in self.steps if s.id != step_id]

        if len(self.steps) < initial_length:
            self._reorder_steps()
            self.updated_at = datetime.utcnow()
            return True
        return False

    def _reorder_steps(self) -> None:
        """Reorder steps after removal."""
        for idx, step in enumerate(self.steps, start=1):
            step.order = idx

    def mark_completed(self) -> None:
        """Mark the routine as completed for today."""
        now = datetime.utcnow()
        self.total_completions += 1
        self.last_completed_at = now
        self.updated_at = now

        # Update streak
        if self.last_completed_at:
            days_since = (now - self.last_completed_at).days
            if days_since <= 1:
                self.current_streak += 1
            else:
                self.current_streak = 1
        else:
            self.current_streak = 1

        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak

        # Reset step completions
        for step in self.steps:
            step.is_completed_today = False

    def mark_step_completed(self, step_id: str) -> bool:
        """Mark a specific step as completed."""
        for step in self.steps:
            if step.id == step_id:
                step.is_completed_today = True
                self.updated_at = datetime.utcnow()
                return True
        return False

    def is_all_steps_completed(self) -> bool:
        """Check if all steps are completed for today."""
        if not self.steps:
            return False
        return all(step.is_completed_today for step in self.steps)

    def get_completion_percentage(self) -> float:
        """Get percentage of steps completed today."""
        if not self.steps:
            return 0.0
        completed = sum(1 for step in self.steps if step.is_completed_today)
        return (completed / len(self.steps)) * 100

    def get_estimated_duration(self) -> int:
        """Get total estimated duration in seconds."""
        return sum(step.duration_seconds or 0 for step in self.steps)

    def activate(self) -> None:
        """Activate the routine."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the routine."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def enable_reminder(self, reminder_time: time) -> None:
        """Enable reminder at specific time."""
        self.reminder_enabled = True
        self.reminder_time = reminder_time
        self.updated_at = datetime.utcnow()

    def disable_reminder(self) -> None:
        """Disable reminder."""
        self.reminder_enabled = False
        self.updated_at = datetime.utcnow()
