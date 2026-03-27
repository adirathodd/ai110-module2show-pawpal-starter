"""Core backend class skeletons for the PawPal+ scheduling system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    recurrence: str = "once"
    due_time: str | None = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as finished."""
        pass

    def update_details(
        self,
        *,
        category: str | None = None,
        duration_minutes: int | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
        due_time: str | None = None,
    ) -> None:
        """Update editable task fields."""
        pass

    def is_due_today(self) -> bool:
        """Return whether this task should appear in today's plan."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        pass

    def list_tasks(self) -> list[Task]:
        """Return the current care tasks for this pet."""
        pass


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: dict[str, Any] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        pass

    def update_preferences(self, preferences: dict[str, Any]) -> None:
        """Replace or merge owner care preferences."""
        pass


class Scheduler:
    def __init__(self, available_minutes: int) -> None:
        self.available_minutes = available_minutes

    def generate_daily_plan(self, owner: Owner, pet: Pet) -> list[Task]:
        """Build an ordered plan for one pet for the current day."""
        pass

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks based on priority and scheduling constraints."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Return tasks that do not fit within the available time."""
        pass
