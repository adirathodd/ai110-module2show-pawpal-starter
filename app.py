import streamlit as st
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = Path(__file__).with_name("data.json")
scheduler = Scheduler()
PRIORITY_BADGES = {
    "high": "🔴 High",
    "medium": "🟡 Medium",
    "low": "🟢 Low",
}

if "persistence_warning" not in st.session_state:
    st.session_state.persistence_warning = None
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    except FileNotFoundError:
        st.session_state.owner = Owner(name="Jordan", available_time=60)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.session_state.owner = Owner(name="Jordan", available_time=60)
        st.session_state.persistence_warning = (
            f"Saved data could not be loaded from {DATA_FILE.name}: {exc}"
        )
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = []
if "generated_conflicts" not in st.session_state:
    st.session_state.generated_conflicts = []
if "overflow_tasks" not in st.session_state:
    st.session_state.overflow_tasks = []


def reset_generated_state() -> None:
    st.session_state.generated_plan = []
    st.session_state.generated_conflicts = []
    st.session_state.overflow_tasks = []


def save_owner_state() -> None:
    st.session_state.owner.save_to_json(DATA_FILE)


def format_priority(priority: str) -> str:
    return PRIORITY_BADGES.get(priority.strip().lower(), priority.title())


def build_task_rows(task_pairs: list[tuple[Pet, Task]]) -> list[dict[str, object]]:
    grouped_tasks: dict[str, list[Task]] = {}
    rows: list[dict[str, object]] = []

    for pet, task in task_pairs:
        grouped_tasks.setdefault(pet.name, []).append(task)

    for pet_name in sorted(grouped_tasks):
        pet_tasks = scheduler.sort_by_time(grouped_tasks[pet_name])
        for task in pet_tasks:
            rows.append(
                {
                    "pet": pet_name,
                    "title": task.title,
                    "date": task.due_date.isoformat(),
                    "time": task.due_time or "Any time",
                    "category": task.category,
                    "duration": task.duration_minutes,
                    "priority": format_priority(task.priority),
                    "frequency": task.recurrence,
                    "completed": task.completed,
                }
            )

    return rows


def build_schedule_rows(schedule_items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for item in schedule_items:
        rows.append(
            {
                "pet": item["pet_name"],
                "task": item["task_title"],
                "time": item["due_time"] or "Any time",
                "duration": item["duration_minutes"],
                "priority": format_priority(str(item["priority"])),
                "category": item["category"],
                "frequency": item["frequency"],
                "why": item["explanation"],
            }
        )

    return rows


def build_overflow_rows(tasks: list[Task]) -> list[dict[str, object]]:
    return [
        {
            "title": task.title,
            "date": task.due_date.isoformat(),
            "time": task.due_time or "Any time",
            "duration": task.duration_minutes,
            "priority": format_priority(task.priority),
        }
        for task in tasks
    ]

st.title("🐾 PawPal+")

if st.session_state.persistence_warning:
    st.warning(st.session_state.persistence_warning)

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
if owner_name.strip():
    normalized_owner_name = owner_name.strip()
    if st.session_state.owner.name != normalized_owner_name:
        st.session_state.owner.name = normalized_owner_name
        save_owner_state()

available_time = st.number_input(
    "Available time today (minutes)",
    min_value=0,
    max_value=24 * 60,
    value=st.session_state.owner.available_time,
)
normalized_available_time = int(available_time)
if st.session_state.owner.available_time != normalized_available_time:
    st.session_state.owner.available_time = normalized_available_time
    save_owner_state()

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=50, value=3)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    try:
        st.session_state.owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        reset_generated_state()
        save_owner_state()
        st.success(f"Added {pet_name.strip()} to {st.session_state.owner.name}'s pets.")
    except (ValueError, KeyError) as exc:
        st.error(str(exc))

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": pet.name, "species": pet.species, "age": pet.age, "task_count": len(pet.tasks)}
            for pet in st.session_state.owner.pets
        ]
    )
else:
    st.info("No pets added yet. Add one to start building a schedule.")

st.markdown("### Tasks")

if st.session_state.owner.pets:
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox(
            "Assign task to",
            options=[pet.name for pet in st.session_state.owner.pets],
        )
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox(
            "Category",
            ["feeding", "exercise", "medication", "grooming", "enrichment", "other"],
        )
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurrence = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        due_time = st.text_input("Due time (HH:MM)", value="08:00")
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        try:
            task_pet = st.session_state.owner.get_pet(selected_pet_name)
            task_pet.add_task(
                Task(
                    title=task_title,
                    category=category,
                    duration_minutes=int(duration),
                    priority=priority,
                    recurrence=recurrence,
                    due_time=due_time.strip() or None,
                )
            )
            reset_generated_state()
            save_owner_state()
            st.success(f"Added task '{task_title.strip()}' for {selected_pet_name}.")
        except (ValueError, KeyError) as exc:
            st.error(str(exc))

    view_col1, view_col2 = st.columns(2)
    with view_col1:
        pet_filter = st.selectbox(
            "View tasks for",
            options=["All pets", *[pet.name for pet in st.session_state.owner.pets]],
        )
    with view_col2:
        status_filter = st.selectbox("Task status", ["All", "Pending", "Completed"])

    completed_filter = None
    if status_filter == "Pending":
        completed_filter = False
    elif status_filter == "Completed":
        completed_filter = True

    filtered_tasks = scheduler.filter_tasks(
        st.session_state.owner,
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed=completed_filter,
    )
    task_rows = build_task_rows(filtered_tasks)

    if task_rows:
        st.write("Current tasks")
        st.caption("Tasks are filtered by your selections and sorted by priority first, then due time within each pet.")
        st.table(task_rows)
    else:
        st.info("No tasks match the current filters.")

    conflict_warnings = scheduler.detect_time_conflicts(st.session_state.owner)
    if conflict_warnings:
        st.warning(
            "Potential scheduling conflicts detected. These tasks are set for the same time, so a pet owner should review and adjust them before relying on the plan."
        )
        st.table([{"warning": warning} for warning in conflict_warnings])
else:
    st.caption("Add a pet first, then you can assign tasks to that pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button uses your backend scheduler to generate a daily plan.")

if st.button("Generate schedule"):
    due_tasks = [task for _, task in st.session_state.owner.get_all_tasks() if task.is_due_today()]
    st.session_state.generated_plan = scheduler.generate_daily_plan(st.session_state.owner)
    st.session_state.generated_conflicts = scheduler.detect_time_conflicts(st.session_state.owner)
    st.session_state.overflow_tasks = scheduler.sort_by_time(
        scheduler.detect_conflicts(due_tasks, st.session_state.owner.available_time)
    )

if st.session_state.generated_plan:
    st.success("Today's plan is ready.")
    st.caption("Today's plan is ranked by priority first, then due time.")
    st.table(build_schedule_rows(st.session_state.generated_plan))
elif st.session_state.owner.pets:
    st.info("Generate a schedule to see the sorted plan for today's due tasks.")

if st.session_state.generated_conflicts:
    st.warning(
        "Some tasks share the same scheduled time. Review these warnings and consider moving one of the tasks to make the day more realistic."
    )
    st.table([{"warning": warning} for warning in st.session_state.generated_conflicts])

if st.session_state.overflow_tasks:
    st.warning("Some due tasks did not fit within the available time today.")
    st.table(build_overflow_rows(st.session_state.overflow_tasks))

    suggested_slot = scheduler.find_next_available_slot(
        st.session_state.owner,
        duration_minutes=st.session_state.overflow_tasks[0].duration_minutes,
        target_date=st.session_state.overflow_tasks[0].due_date,
    )
    if suggested_slot is not None:
        st.info(
            f"Suggested next available slot for '{st.session_state.overflow_tasks[0].title}': "
            f"{st.session_state.overflow_tasks[0].due_date.isoformat()} at {suggested_slot}."
        )
    else:
        st.warning("No additional open slot is available today for the first unscheduled task.")
elif st.session_state.owner.pets and st.session_state.generated_plan:
    st.success("All due tasks fit within today's available time.")
