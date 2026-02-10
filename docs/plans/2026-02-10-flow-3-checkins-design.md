# Flow 3 Design: Weekly Team Check-ins and Reports

## Summary
Add weekly team check-ins with structured fields and auto metrics. Students submit one check-in per team per week. Teachers review, comment, and approve. Add a progress bar in the student form and a reports window with charts (Gantt, burndown, progress over time) built with Matplotlib and Seaborn, using NumPy for simple aggregations.

## Scope
In scope:
- Student: submit weekly team check-in with status and text fields.
- Student: see progress bar and current metrics before submit.
- Teacher: view check-ins list, open details, comment, approve.
- Teacher: on-demand reports window with team selector and charts.

Out of scope:
- Blockers.
- File uploads or grading.
- Notifications.

## UX Flow
Student:
1. Select team in Student dashboard.
2. See progress bar and auto metrics (done/total, %).
3. Fill check-in form: status (Green/Yellow/Red), wins, risks, next goal, help needed.
4. Submit weekly check-in.
5. See check-in row in a table.

Teacher:
1. Open Check-ins tab in Teacher dashboard.
2. See table of check-ins (team, week, status, % complete, submitted at).
3. Select a row to see details in the drawer.
4. Add comment or approve.
5. Open Reports window and select a team to view charts.

## Data Model
Add tables:

- `checkins`
  - `id` INTEGER PK
  - `team_id` INTEGER FK
  - `week_start` TEXT
  - `week_end` TEXT
  - `status` TEXT
  - `wins` TEXT
  - `risks` TEXT
  - `next_goal` TEXT
  - `help_needed` TEXT NULL
  - `metrics_total` INTEGER
  - `metrics_done` INTEGER
  - `metrics_percent` INTEGER
  - `submitted_at` TEXT

- `checkin_comments`
  - `id` INTEGER PK
  - `checkin_id` INTEGER FK
  - `author` TEXT
  - `text` TEXT
  - `created_at` TEXT
  - `kind` TEXT (comment | approval)

Rule: one check-in per team per week. If a check-in exists for the current week, block duplicate submission or route to edit.

## Services
Add `CheckinService` with:
- `create_checkin(team_id, week_start, week_end, data, metrics)`
- `list_checkins_for_class(class_id)`
- `list_checkins_for_team(team_id)`
- `get_checkin(checkin_id)`
- `add_checkin_comment(checkin_id, author, text, kind)`
- `list_checkin_comments(checkin_id)`

Metrics:
- `metrics_total` = sum of task weights
- `metrics_done` = sum of weights where status == Done
- `metrics_percent` = round(done / total * 100)

## UI Components
Student:
- Add a Check-ins section in Student dashboard (tab or panel).
- Check-in form uses model form system (multi-field).
- Progress bar shows `metrics_percent`.

Teacher:
- Add Check-ins tab next to Teams/Roadmaps.
- Table uses DataTable; drawer shows full check-in details and comments.
- Add comment/approve modal using form system.

Reports window:
- Team selector (combobox).
- Charts:
  - Gantt (weights as durations)
  - Burndown (remaining weight)
  - Progress over time (from check-ins)
- Use Seaborn style and Matplotlib canvas in Tk.

## Validation
- Status required (Green/Yellow/Red).
- Wins, risks, next goal required.
- Help needed optional.
- Validate that a roadmap exists and has tasks before submit.

## Error Handling
- Show warnings for missing or invalid fields.
- Handle empty task lists by displaying 0% and empty charts.
- Protect against duplicate weekly submissions.

## Dependencies
- Add `numpy` and `seaborn` to `requirements.txt`.
- Use Matplotlib already in use.

## Testing
- Service tests for metrics and weekly duplicate rule.
- UI smoke tests: submit check-in, teacher review, charts open.

## Migration
- Add `checkins` and `checkin_comments` tables in `schema.py` with safe migration.

## Open Questions
- Should teachers edit a submitted check-in or only comment/approve?
- Should the weekly rule block duplicates or allow overwrite?
