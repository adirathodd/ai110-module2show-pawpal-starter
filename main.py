"""CLI demo script for verifying PawPal+ scheduling behavior."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(schedule: list[dict[str, object]]) -> None:
    print("Today's Schedule")
    print("=" * 40)

    if not schedule:
        print("No tasks fit within the available time.")
        return

    for index, item in enumerate(schedule, start=1):
        due_time = item["due_time"] or "Any time"
        print(f"{index}. {item['task_title']} for {item['pet_name']}")
        print(
            f"   Time: {due_time} | Duration: {item['duration_minutes']} min | "
            f"Priority: {item['priority']}"
        )
        print(f"   Category: {item['category']} | Frequency: {item['frequency']}")
        print(f"   Why: {item['explanation']}")


def print_task_list(
    title: str,
    task_items: list[Task] | list[tuple[Pet, Task]],
    pet_name: str | None = None,
) -> None:
    print()
    print(title)
    print("-" * 40)

    if not task_items:
        print("No tasks to show.")
        return

    for index, item in enumerate(task_items, start=1):
        if isinstance(item, tuple):
            pet, task = item
            pet_label = pet.name
        else:
            task = item
            pet_label = pet_name or "N/A"

        due_time = task.due_time or "Any time"
        status = "complete" if task.completed else "pending"
        print(
            f"{index}. {task.title} | Pet: {pet_label} | Date: {task.due_date.isoformat()} | "
            f"Time: {due_time} | Priority: {task.priority} | Status: {status}"
        )


def main() -> None:
    owner = Owner(name="Jordan", available_time=60)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)

    mochi.add_task(
        Task(
            title="Morning walk",
            category="exercise",
            duration_minutes=25,
            priority="high",
            recurrence="daily",
            due_time="08:00",
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast",
            category="feeding",
            duration_minutes=10,
            priority="high",
            recurrence="daily",
            due_time="07:30",
        )
    )
    mochi.add_task(
        Task(
            title="Training session",
            category="enrichment",
            duration_minutes=15,
            priority="medium",
            recurrence="daily",
            due_time="09:00",
        )
    )
    luna.add_task(
        Task(
            title="Play session",
            category="enrichment",
            duration_minutes=20,
            priority="medium",
            recurrence="daily",
            due_time="18:00",
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
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler()
    next_walk = mochi.mark_task_complete("Morning walk", completion_date=date.today())

    print_task_list("Mochi Tasks As Added", mochi.list_tasks(), pet_name=mochi.name)
    print_task_list(
        "Mochi Tasks Sorted By Time",
        scheduler.sort_by_time(mochi.list_tasks()),
        pet_name=mochi.name,
    )
    if next_walk is not None:
        print_task_list("Next Recurring Walk", [next_walk], pet_name=mochi.name)
    print_task_list(
        "Pending Tasks For Luna",
        scheduler.filter_tasks(owner, pet_name="Luna", completed=False),
    )
    print_task_list("Completed Tasks Across All Pets", scheduler.filter_tasks(owner, completed=True))

    conflict_warnings = scheduler.detect_time_conflicts(owner)
    print()
    print("Conflict Warnings")
    print("-" * 40)
    if conflict_warnings:
        for warning in conflict_warnings:
            print(warning)
    else:
        print("No time conflicts detected.")

    todays_schedule = scheduler.generate_daily_plan(owner)
    print()
    print_schedule(todays_schedule)


if __name__ == "__main__":
    main()
