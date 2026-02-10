# MVP Design: Teacher-to-Student Project Management App (Tkinter)

## Scope
Build a desktop MVP that supports:
- Teacher class setup, student roster, and manual team formation
- Student roadmap builder with phases and tasks
- Roadmap approval gate (Draft → Submitted → Approved)
- Task status updates and update logs after approval
- Team Gantt and Burndown charts

## Architecture
Use a small MVC-style layout:
- `ui/` Tkinter frames per screen
- `services/` database and validation logic
- `models/` dataclasses for core entities
- `db/` schema initialization and seed helpers

The app starts with a role selection screen, then loads the Teacher or Student dashboard.

## Data Model (SQLite)
Tables:
- `users(id, name, email, role)`
- `classes(id, name, term)`
- `teams(id, class_id, name, principal_user_id)`
- `team_members(team_id, user_id)`
- `roadmaps(id, team_id, status, created_at)`
- `phases(id, roadmap_id, name, sort_order)`
- `tasks(id, phase_id, title, weight, status, assignee_user_id, notes)`
- `updates(id, task_id, user_id, text, created_at)`

Roadmap status is one of `Draft`, `Submitted`, `Approved`.

## UI Flow
**Role Selection**
- Choose `Teacher` or `Student`.

**Teacher Dashboard**
- Create class (name, term)
- Add students (name, email)
- Create teams, assign members, set principal student
- Review roadmaps and approve/reject with comments
- View class-level charts

**Student Dashboard**
- Select team
- Build roadmap in a Treeview (phases → tasks)
- Submit roadmap for approval
- After approval, update task status and log updates
- View team Gantt and Burndown charts

## Validation Rules
- Roadmap must have at least 3 phases and at least 1 task per phase to submit
- Sum of task weights must be > 0; warn if not 100
- Only principal student can submit the roadmap
- Only teacher can approve
- Task status updates allowed only when roadmap is approved

## Data Flow
UI → Service → DB → UI refresh. Services validate inputs, perform SQL operations, and return structured results. UI uses message dialogs for success and error states.

## Error Handling
- Catch DB errors and show a clear message
- Block actions when required selections are missing
- Confirm destructive actions (delete phase/task/team)

## Testing
- Manual smoke test checklist
- Optional unit tests for roadmap validation logic
