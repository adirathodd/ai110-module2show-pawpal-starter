from datetime import date, timedelta
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_sets_task_status_to_true() -> None:
    task = Task(
        title="Evening medication",
        category="medication",
        duration_minutes=5,
        priority="high",
        recurrence="daily",
        due_time="18:00",
    )

    task.mark_complete()

    assert task.completed is True


def test_sort_by_time_prioritizes_urgency_before_due_time() -> None:
    scheduler = Scheduler()
    tasks = [
        Task(
            title="Evening walk",
            category="exercise",
            duration_minutes=20,
            priority="low",
            due_time="18:00",
        ),
        Task(
            title="Breakfast",
            category="feeding",
            duration_minutes=10,
            priority="medium",
            due_time="07:30",
        ),
        Task(
            title="Medication",
            category="medication",
            duration_minutes=5,
            priority="high",
            due_time="09:00",
        ),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.title for task in sorted_tasks] == ["Medication", "Breakfast", "Evening walk"]


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        title="Morning walk",
        category="exercise",
        duration_minutes=20,
        priority="high",
        recurrence="daily",
        due_time="08:00",
    )

    starting_count = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == starting_count + 1


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        title="Morning walk",
        category="exercise",
        duration_minutes=20,
        priority="high",
        recurrence="daily",
        due_time="08:00",
        due_date=date.today(),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete("Morning walk", completion_date=date.today())

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_detect_time_conflicts_returns_warning_message() -> None:
    owner = Owner(name="Jordan", available_time=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    mochi.add_task(
        Task(
            title="Training session",
            category="enrichment",
            duration_minutes=15,
            priority="medium",
            recurrence="daily",
            due_time="09:00",
            due_date=date.today(),
        )
    )
    luna.add_task(
        Task(
            title="Medication",
            category="medication",
            duration_minutes=5,
            priority="high",
            recurrence="daily",
            due_time="09:00",
            due_date=date.today(),
        )
    )
    owner.add_pet(mochi)
    owner.add_pet(luna)

    warnings = Scheduler().detect_time_conflicts(owner)

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "multiple pets" in warnings[0]


def test_owner_save_and_load_round_trip(tmp_path: Path) -> None:
    owner = Owner(name="Jordan", available_time=75, preferences={"focus": "morning"})
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(
        Task(
            title="Morning walk",
            category="exercise",
            duration_minutes=20,
            priority="high",
            recurrence="daily",
            due_time="08:00",
            due_date=date.today(),
        )
    )
    pet.add_task(
        Task(
            title="Brush coat",
            category="grooming",
            duration_minutes=10,
            priority="low",
            recurrence="weekly",
            due_time=None,
            due_date=date.today() + timedelta(days=2),
            completed=True,
        )
    )
    owner.add_pet(pet)

    data_file = tmp_path / "data.json"
    owner.save_to_json(data_file)

    restored_owner = Owner.load_from_json(data_file)

    assert restored_owner.name == "Jordan"
    assert restored_owner.available_time == 75
    assert restored_owner.preferences == {"focus": "morning"}
    assert len(restored_owner.pets) == 1
    assert restored_owner.pets[0].name == "Mochi"
    assert len(restored_owner.pets[0].tasks) == 2
    assert restored_owner.pets[0].tasks[0].due_date == date.today()
    assert restored_owner.pets[0].tasks[1].completed is True


def test_find_next_available_slot_returns_earliest_open_time() -> None:
    owner = Owner(
        name="Jordan",
        available_time=120,
        preferences={"day_start": "07:00", "day_end": "10:00"},
    )
    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_task(
        Task(
            title="Breakfast",
            category="feeding",
            duration_minutes=10,
            priority="high",
            due_time="07:30",
            due_date=date.today(),
        )
    )
    mochi.add_task(
        Task(
            title="Walk",
            category="exercise",
            duration_minutes=25,
            priority="high",
            due_time="08:00",
            due_date=date.today(),
        )
    )
    mochi.add_task(
        Task(
            title="Training",
            category="enrichment",
            duration_minutes=15,
            priority="medium",
            due_time="09:00",
            due_date=date.today(),
        )
    )
    owner.add_pet(mochi)

    slot = Scheduler().find_next_available_slot(owner, duration_minutes=20, target_date=date.today())

    assert slot == "07:00"


def test_find_next_available_slot_returns_earliest_gap() -> None:
    owner = Owner(
        name="Jordan",
        available_time=180,
        preferences={"day_start": "08:00", "day_end": "12:00"},
    )
    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_task(
        Task(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority="high",
            due_time="08:00",
            due_date=date.today(),
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast",
            category="feeding",
            duration_minutes=30,
            priority="high",
            due_time="09:00",
            due_date=date.today(),
        )
    )
    owner.add_pet(mochi)

    slot = Scheduler().find_next_available_slot(owner, duration_minutes=20, target_date=date.today())

    assert slot == "08:30"
