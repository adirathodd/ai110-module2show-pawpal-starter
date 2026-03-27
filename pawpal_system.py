"""Core backend models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    recurrence: str = "once"
    due_time: str | None = None
    completed: bool = False

    PRIORITY_ORDER: ClassVar[dict[str, int]] = {"high": 0, "medium": 1, "low": 2}

    def __post_init__(self) -> None:
        """Normalize and validate task fields after initialization."""
        self.title = self.title.strip()
        self.category = self.category.strip().lower()
        self.priority = self.priority.strip().lower()
        self.recurrence = self.recurrence.strip().lower()

        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if not self.category:
            raise ValueError("Task category cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than zero.")
        if self.priority not in self.PRIORITY_ORDER:
            raise ValueError("Task priority must be 'low', 'medium', or 'high'.")
        if not self.recurrence:
            raise ValueError("Task recurrence cannot be empty.")
        if self.due_time is not None:
            self.due_time = self._normalize_due_time(self.due_time)

    @property
    def description(self) -> str:
        """Compatibility alias for the task title."""
        return self.title

    @property
    def frequency(self) -> str:
        """Compatibility alias for recurrence."""
        return self.recurrence

    @property
    def time(self) -> str | None:
        """Compatibility alias for due time."""
        return self.due_time

    def mark_complete(self) -> None:
        """Mark the task as finished."""
        self.completed = True

    def update_details(
        self,
        *,
        title: str | None = None,
        category: str | None = None,
        duration_minutes: int | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
        due_time: str | None = None,
        completed: bool | None = None,
    ) -> None:
        """Update editable task fields."""
        if title is not None:
            cleaned_title = title.strip()
            if not cleaned_title:
                raise ValueError("Task title cannot be empty.")
            self.title = cleaned_title

        if category is not None:
            cleaned_category = category.strip().lower()
            if not cleaned_category:
                raise ValueError("Task category cannot be empty.")
            self.category = cleaned_category

        if duration_minutes is not None:
            if duration_minutes <= 0:
                raise ValueError("Task duration must be greater than zero.")
            self.duration_minutes = duration_minutes

        if priority is not None:
            cleaned_priority = priority.strip().lower()
            if cleaned_priority not in self.PRIORITY_ORDER:
                raise ValueError("Task priority must be 'low', 'medium', or 'high'.")
            self.priority = cleaned_priority

        if recurrence is not None:
            cleaned_recurrence = recurrence.strip().lower()
            if not cleaned_recurrence:
                raise ValueError("Task recurrence cannot be empty.")
            self.recurrence = cleaned_recurrence

        if due_time is not None:
            self.due_time = self._normalize_due_time(due_time)

        if completed is not None:
            self.completed = completed

    def is_due_today(self) -> bool:
        """Return whether this task should appear in today's plan."""
        return not self.completed

    def priority_rank(self) -> int:
        """Lower values represent higher urgency."""
        return self.PRIORITY_ORDER[self.priority]

    @staticmethod
    def _normalize_due_time(value: str) -> str:
        """Validate and normalize a due time to HH:MM format."""
        text = value.strip()
        if not text:
            raise ValueError("Due time cannot be empty.")

        try:
            hours_text, minutes_text = text.split(":", maxsplit=1)
            hours = int(hours_text)
            minutes = int(minutes_text)
        except ValueError as exc:
            raise ValueError("Due time must use HH:MM 24-hour format.") from exc

        if hours not in range(24) or minutes not in range(60):
            raise ValueError("Due time must use HH:MM 24-hour format.")

        return f"{hours:02d}:{minutes:02d}"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate pet fields after initialization."""
        self.name = self.name.strip()
        self.species = self.species.strip().lower()

        if not self.name:
            raise ValueError("Pet name cannot be empty.")
        if not self.species:
            raise ValueError("Pet species cannot be empty.")
        if self.age < 0:
            raise ValueError("Pet age cannot be negative.")

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        if any(existing.title == task.title for existing in self.tasks):
            raise ValueError(f"Task '{task.title}' already exists for {self.name}.")
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        for index, task in enumerate(self.tasks):
            if task.title == task_title:
                del self.tasks[index]
                return
        raise KeyError(f"Task '{task_title}' was not found for {self.name}.")

    def list_tasks(self) -> list[Task]:
        """Return the current care tasks for this pet."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: dict[str, Any] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize and validate owner fields after initialization."""
        self.name = self.name.strip()

        if not self.name:
            raise ValueError("Owner name cannot be empty.")
        if self.available_time < 0:
            raise ValueError("Available time cannot be negative.")

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        if any(existing.name == pet.name for existing in self.pets):
            raise ValueError(f"Pet '{pet.name}' is already linked to {self.name}.")
        self.pets.append(pet)

    def update_preferences(self, preferences: dict[str, Any]) -> None:
        """Merge new owner preferences into the existing set."""
        self.preferences.update(preferences)

    def get_pet(self, pet_name: str) -> Pet:
        """Return a pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        raise KeyError(f"Pet '{pet_name}' was not found for {self.name}.")

    def get_all_tasks(self, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Return tasks across every pet owned by this owner."""
        tasks: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                if include_completed or not task.completed:
                    tasks.append((pet, task))
        return tasks


class Scheduler:
    """Task-planning engine for one owner's pets."""

    def generate_daily_plan(
        self,
        owner: Owner,
        pet: Pet | None = None,
    ) -> list[dict[str, Any]]:
        """Build an ordered plan for one pet or all pets for the current day."""
        task_pairs = self._get_due_tasks(owner, pet)
        ranked_pairs = sorted(task_pairs, key=self._pair_sort_key)

        plan: list[dict[str, Any]] = []
        time_used = 0

        for current_pet, task in ranked_pairs:
            if time_used + task.duration_minutes > owner.available_time:
                continue

            plan.append(
                {
                    "pet_name": current_pet.name,
                    "task_title": task.title,
                    "category": task.category,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "due_time": task.due_time,
                    "frequency": task.recurrence,
                    "completed": task.completed,
                    "explanation": self._build_explanation(current_pet, task),
                }
            )
            time_used += task.duration_minutes

        return plan

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks based on priority, due time, and duration."""
        return sorted(tasks, key=self._task_sort_key)

    def detect_conflicts(self, tasks: list[Task], available_minutes: int) -> list[Task]:
        """Return ranked tasks that do not fit within the available time."""
        ranked_tasks = self.rank_tasks(tasks)
        conflicts: list[Task] = []
        time_used = 0

        for task in ranked_tasks:
            if time_used + task.duration_minutes <= available_minutes:
                time_used += task.duration_minutes
            else:
                conflicts.append(task)

        return conflicts

    def _get_due_tasks(
        self,
        owner: Owner,
        pet: Pet | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Collect due tasks for one pet or every pet owned by the owner."""
        if pet is not None:
            if pet not in owner.pets:
                raise ValueError("The selected pet does not belong to this owner.")
            return [(pet, task) for task in pet.tasks if task.is_due_today()]

        return [(current_pet, task) for current_pet, task in owner.get_all_tasks() if task.is_due_today()]

    def _pair_sort_key(self, item: tuple[Pet, Task]) -> tuple[int, int, int, str, str]:
        """Build the ordering key for a pet-task pair."""
        pet, task = item
        return (*self._task_sort_key(task), pet.name.lower())

    def _task_sort_key(self, task: Task) -> tuple[int, int, int, str]:
        """Build the ordering key for an individual task."""
        return (
            task.priority_rank(),
            self._due_time_rank(task.due_time),
            task.duration_minutes,
            task.title.lower(),
        )

    def _due_time_rank(self, due_time: str | None) -> int:
        """Convert an optional due time into a sortable minute offset."""
        if due_time is None:
            return 24 * 60 + 1

        hours_text, minutes_text = due_time.split(":", maxsplit=1)
        return int(hours_text) * 60 + int(minutes_text)

    def _build_explanation(self, pet: Pet, task: Task) -> str:
        """Create a short human-readable explanation for a scheduled task."""
        if task.due_time is not None:
            return (
                f"Scheduled for {pet.name} because it is a {task.priority}-priority "
                f"{task.category} task due by {task.due_time} and it fits in the available time."
            )

        return (
            f"Scheduled for {pet.name} because it is a {task.priority}-priority "
            f"{task.category} task that fits in the available time."
        )
