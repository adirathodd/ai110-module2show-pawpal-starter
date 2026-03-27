"""CLI demo script for verifying PawPal+ scheduling behavior."""

from datetime import date

from cli_output import (
    format_priority,
    format_section_heading,
    format_status,
    format_title,
    render_kv_summary,
    render_table,
)
from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(schedule: list[dict[str, object]]) -> None:
    print()
    print(format_section_heading("Today's Schedule", icon="🗓️"))

    if not schedule:
        print("No tasks fit within the available time.")
        return

    rows = [
        [
            item["pet_name"],
            format_title(str(item["task_title"]), str(item["category"])),
            item["due_time"] or "Any time",
            f"{item['duration_minutes']} min",
            format_priority(str(item["priority"])),
            item["frequency"],
            item["explanation"],
        ]
        for item in schedule
    ]
    print(
        render_table(
            ["Pet", "Task", "Time", "Duration", "Priority", "Frequency", "Why It Was Chosen"],
            rows,
        )
    )


def print_task_list(
    title: str,
    task_items: list[Task] | list[tuple[Pet, Task]],
    pet_name: str | None = None,
) -> None:
    print()
    print(format_section_heading(title, icon="📋"))

    if not task_items:
        print("No tasks to show.")
        return

    rows: list[list[object]] = []
    for index, item in enumerate(task_items, start=1):
        if isinstance(item, tuple):
            pet, task = item
            pet_label = pet.name
        else:
            task = item
            pet_label = pet_name or "N/A"

        rows.append(
            [
                index,
                pet_label,
                format_title(task.title, task.category),
                task.due_date.isoformat(),
                task.due_time or "Any time",
                f"{task.duration_minutes} min",
                format_priority(task.priority),
                format_status(task.completed),
            ]
        )

    print(render_table(["#", "Pet", "Task", "Date", "Time", "Duration", "Priority", "Status"], rows))


def print_conflicts(conflict_warnings: list[str]) -> None:
    print()
    print(format_section_heading("Conflict Warnings", icon="⚠️"))

    if not conflict_warnings:
        print("No time conflicts detected.")
        return

    rows = [[index, warning] for index, warning in enumerate(conflict_warnings, start=1)]
    print(render_table(["#", "Warning"], rows))


def print_next_slot(next_slot: str | None) -> None:
    print()
    print(format_section_heading("Next Available Slot", icon="⏰"))
    if next_slot is not None:
        print(f"The earliest 20-minute opening is {next_slot}.")
    else:
        print("No open slot is available for a 20-minute task today.")


def main() -> None:
    owner = Owner(
        name="Jordan",
        available_time=60,
        preferences={"day_start": "07:00", "day_end": "20:00"},
    )

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

    print(format_section_heading("PawPal+ Daily Assistant", icon="🐾"))
    print(
        render_kv_summary(
            [
                ("Owner", owner.name),
                ("Pets", ", ".join(pet.name for pet in owner.pets)),
                ("Available time", f"{owner.available_time} minutes"),
                ("Date", date.today().isoformat()),
            ]
        )
    )

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
    print_conflicts(conflict_warnings)

    next_slot = scheduler.find_next_available_slot(owner, duration_minutes=20)
    print_next_slot(next_slot)

    todays_schedule = scheduler.generate_daily_plan(owner)
    print_schedule(todays_schedule)


if __name__ == "__main__":
    main()
