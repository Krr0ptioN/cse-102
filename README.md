# Project Lifecycle Engine (MVP)

A Tkinter desktop app for managing student project roadmaps, approvals, and progress tracking.

## Requirements

- Python 3.11+
- Tkinter (bundled with most Python installs)
- `matplotlib`
- `pandas`

Install deps:

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

## MVP Workflow

1. Teacher creates a class and adds students.
2. Teacher creates teams and assigns members.
3. Student builds a roadmap with phases and tasks.
4. Student submits roadmap for approval.
5. Teacher approves the roadmap.
6. Students update task status and log updates.
7. Charts show Gantt and Burndown views.
