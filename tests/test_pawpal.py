from pawpal_system import Pet, Task


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
