"""CLI demo script for verifying PawPal+ scheduling behavior."""

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


def main() -> None:
    owner = Owner(name="Jordan", available_time=60)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)

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
            title="Morning walk",
            category="exercise",
            duration_minutes=25,
            priority="high",
            recurrence="daily",
            due_time="08:00",
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

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler()
    todays_schedule = scheduler.generate_daily_plan(owner)
    print_schedule(todays_schedule)


if __name__ == "__main__":
    main()
