from datetime import date, timedelta

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


def test_sort_by_time_returns_tasks_in_chronological_order() -> None:
    scheduler = Scheduler()
    tasks = [
        Task(
            title="Evening walk",
            category="exercise",
            duration_minutes=20,
            priority="medium",
            due_time="18:00",
        ),
        Task(
            title="Breakfast",
            category="feeding",
            duration_minutes=10,
            priority="high",
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

    assert [task.title for task in sorted_tasks] == ["Breakfast", "Medication", "Evening walk"]


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
