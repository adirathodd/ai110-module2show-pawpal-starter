# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- Multi-pet task management through `Owner`, `Pet`, `Task`, and `Scheduler` classes
- Priority-based task sorting with due time as the tie-breaker
- Task filtering by pet name and completion status
- Daily and weekly recurring task generation after completion
- Exact-time conflict warnings for overlapping scheduled task times
- Available-time-aware daily plan generation
- Next available slot recommendation for fitting a new task into the day

## Smarter Scheduling

PawPal+ now includes a lightweight scheduling layer that makes the app more useful for day-to-day pet care planning:

- Tasks are scheduled by priority first and then by due time so urgent care appears first.
- Tasks can be filtered by pet name or completion status.
- Daily and weekly recurring tasks automatically create the next occurrence when completed.
- The scheduler can detect exact time conflicts and return warning messages instead of stopping the program.
- The Streamlit task tables use visual priority badges such as `🔴 High` and `🟡 Medium`.
- The daily plan still respects the owner's available time while prioritizing urgent tasks.
- The scheduler can recommend the next available slot for a new task based on today's scheduled items.
- The CLI demo now uses emoji-enhanced task labels, color-coded status and priority labels, and structured tables.

## CLI Demo

Run the terminal demo with:

```bash
python main.py
```

The demo prints formatted task tables, conflict warnings, next-slot guidance, and a cleaner daily schedule summary.

## Agent Mode Extension

For the optional extension, Agent Mode was used to review the current codebase and recommend an advanced feature that fit the existing models without forcing a large redesign. Based on that review, I added a `find_next_available_slot(...)` scheduler method that looks at scheduled task times and durations, then suggests the earliest open time window for a new task. After the recommendation step, the implementation was completed with a matching CLI demo and automated pytest coverage.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

The test suite covers task completion, task addition, priority-first scheduling, recurring daily task creation, duplicate-time conflict warnings, and next-available-slot suggestions.

Confidence Level: 4/5 stars. The core scheduling behaviors are covered and currently passing, but the system still uses a lightweight conflict model and does not yet test every UI interaction or every possible edge case.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
