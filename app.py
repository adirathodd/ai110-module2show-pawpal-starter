import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=60)

st.title("🐾 PawPal+")

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
    st.session_state.owner.name = owner_name.strip()

available_time = st.number_input(
    "Available time today (minutes)",
    min_value=0,
    max_value=24 * 60,
    value=st.session_state.owner.available_time,
)
st.session_state.owner.available_time = int(available_time)

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
            st.success(f"Added task '{task_title.strip()}' for {selected_pet_name}.")
        except (ValueError, KeyError) as exc:
            st.error(str(exc))

    task_rows = []
    for pet in st.session_state.owner.pets:
        for task in pet.list_tasks():
            task_rows.append(
                {
                    "pet": pet.name,
                    "title": task.title,
                    "category": task.category,
                    "time": task.due_time or "Any time",
                    "duration": task.duration_minutes,
                    "priority": task.priority,
                    "frequency": task.recurrence,
                    "completed": task.completed,
                }
            )

    if task_rows:
        st.write("Current tasks:")
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.caption("Add a pet first, then you can assign tasks to that pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button uses your backend scheduler to generate a daily plan.")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    daily_plan = scheduler.generate_daily_plan(st.session_state.owner)

    if daily_plan:
        st.write("Today's schedule:")
        st.table(daily_plan)
    else:
        st.warning("No tasks could be scheduled with the current pets, tasks, and available time.")
