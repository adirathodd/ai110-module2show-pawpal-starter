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

## Smarter Scheduling

PawPal+ now includes a lightweight scheduling layer that makes the app more useful for day-to-day pet care planning:

- Tasks can be sorted by time so earlier care items appear first.
- Tasks can be filtered by pet name or completion status.
- Daily and weekly recurring tasks automatically create the next occurrence when completed.
- The scheduler can detect exact time conflicts and return warning messages instead of stopping the program.
- The daily plan still respects the owner's available time while prioritizing urgent tasks.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

The test suite covers task completion, task addition, chronological sorting, recurring daily task creation, and duplicate-time conflict warnings.

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
