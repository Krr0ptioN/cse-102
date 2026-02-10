# MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Tkinter desktop MVP for teacher-to-student project management with roadmaps, approvals, and charts.

**Architecture:** Small MVC layout with Tkinter frames for UI, service modules for DB/validation, and SQLite for persistence. Role selection screen routes to Teacher or Student dashboards.

**Tech Stack:** Python 3, Tkinter, SQLite3, Matplotlib, pandas, pytest.

---

### Task 1: Create project skeleton and dependency list

**Files:**
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/db/__init__.py`
- Create: `app/services/__init__.py`
- Create: `app/ui/__init__.py`
- Create: `requirements.txt`

**Step 1: Create empty package files**

**Step 2: Add dependency list**

```
matplotlib
pandas
```

**Step 3: Commit**

```bash
git add app requirements.txt
git commit -m "chore: add app skeleton"
```

---

### Task 2: Define SQLite schema and init function

**Files:**
- Create: `app/db/schema.py`
- Test: `tests/test_schema.py`

**Step 1: Write failing test**

```python
def test_schema_creates_tables(tmp_path):
    from app.db.schema import init_db, list_tables
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    tables = set(list_tables(str(db_path)))
    assert {"users", "classes", "teams", "team_members", "roadmaps", "phases", "tasks", "updates"}.issubset(tables)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_schema.py::test_schema_creates_tables -v`
Expected: FAIL with import error or missing functions

**Step 3: Write minimal implementation**

```python
import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (...);
...;
"""

def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

def list_tables(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_schema.py::test_schema_creates_tables -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/db/schema.py tests/test_schema.py
git commit -m "feat: add sqlite schema init"
```

---

### Task 3: Add DB connection helper

**Files:**
- Create: `app/db/connection.py`
- Test: `tests/test_connection.py`

**Step 1: Write failing test**

```python
def test_connection_executes_query(tmp_path):
    from app.db.connection import get_connection
    db_path = tmp_path / "app.db"
    conn = get_connection(str(db_path))
    conn.execute("CREATE TABLE t(id INTEGER)")
    conn.execute("INSERT INTO t(id) VALUES (1)")
    conn.commit()
    row = conn.execute("SELECT id FROM t").fetchone()
    assert row[0] == 1
    conn.close()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_connection.py::test_connection_executes_query -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_connection.py::test_connection_executes_query -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/db/connection.py tests/test_connection.py
git commit -m "feat: add db connection helper"
```

---

### Task 4: Add roadmap validation logic

**Files:**
- Create: `app/services/validation.py`
- Test: `tests/test_validation.py`

**Step 1: Write failing tests**

```python
from app.services.validation import validate_roadmap

def test_roadmap_requires_three_phases():
    result = validate_roadmap(phases=[{"tasks": [1]}])
    assert result["ok"] is False


def test_roadmap_requires_task_per_phase():
    result = validate_roadmap(phases=[{"tasks": [1]}, {"tasks": []}, {"tasks": [1]}])
    assert result["ok"] is False


def test_roadmap_weight_warning():
    result = validate_roadmap(phases=[{"tasks": [20]}, {"tasks": [20]}, {"tasks": [10]}])
    assert result["ok"] is True
    assert result["weight_warning"] is True
```

**Step 2: Run tests to verify failure**

Run: `pytest tests/test_validation.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def validate_roadmap(phases: list[dict]) -> dict:
    if len(phases) < 3:
        return {"ok": False, "reason": "Need at least 3 phases"}
    for phase in phases:
        if not phase.get("tasks"):
            return {"ok": False, "reason": "Each phase needs a task"}
    total = sum(sum(phase["tasks"]) for phase in phases)
    return {"ok": True, "weight_warning": total != 100}
```

**Step 4: Run tests to verify pass**

Run: `pytest tests/test_validation.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/validation.py tests/test_validation.py
git commit -m "feat: add roadmap validation"
```

---

### Task 5: Build core DB services (users, classes, teams)

**Files:**
- Create: `app/services/class_service.py`
- Test: `tests/test_class_service.py`

**Step 1: Write failing test**

```python
def test_create_class_and_user(tmp_path):
    from app.db.schema import init_db
    from app.services.class_service import create_class, create_user
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    class_id = create_class(str(db_path), "CSE 102", "Spring 2026")
    user_id = create_user(str(db_path), "Ava", "ava@example.com", "student")
    assert class_id > 0
    assert user_id > 0
```

**Step 2: Run test to verify failure**

Run: `pytest tests/test_class_service.py::test_create_class_and_user -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement `create_class`, `create_user`, and `list_users`.

**Step 4: Run tests to verify pass**

Run: `pytest tests/test_class_service.py::test_create_class_and_user -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/class_service.py tests/test_class_service.py
git commit -m "feat: add class and user services"
```

---

### Task 6: Build roadmap services (create, submit, approve)

**Files:**
- Create: `app/services/roadmap_service.py`
- Test: `tests/test_roadmap_service.py`

**Step 1: Write failing test**

```python
def test_submit_and_approve(tmp_path):
    from app.db.schema import init_db
    from app.services.roadmap_service import create_roadmap, submit_roadmap, approve_roadmap, get_roadmap_status
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    roadmap_id = create_roadmap(str(db_path), team_id=1)
    submit_roadmap(str(db_path), roadmap_id)
    assert get_roadmap_status(str(db_path), roadmap_id) == "Submitted"
    approve_roadmap(str(db_path), roadmap_id)
    assert get_roadmap_status(str(db_path), roadmap_id) == "Approved"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/test_roadmap_service.py::test_submit_and_approve -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement roadmap status transitions and basic lookup.

**Step 4: Run tests to verify pass**

Run: `pytest tests/test_roadmap_service.py::test_submit_and_approve -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/roadmap_service.py tests/test_roadmap_service.py
git commit -m "feat: add roadmap status services"
```

---

### Task 7: Create base Tkinter app and role selection

**Files:**
- Modify: `app/main.py`
- Create: `app/ui/role_select.py`

**Step 1: Add minimal UI shell**
- Tk root window
- Role selection buttons
- Simple frame swap helper

**Step 2: Manual verification**

Run: `python -m app.main`
Expected: Window opens with Teacher and Student buttons

**Step 3: Commit**

```bash
git add app/main.py app/ui/role_select.py
git commit -m "feat: add role selection screen"
```

---

### Task 8: Teacher dashboard basics

**Files:**
- Create: `app/ui/teacher_dashboard.py`
- Modify: `app/main.py`

**Step 1: Build Teacher dashboard layout**
- Class panel
- Student list panel
- Team panel
- Roadmap review panel

**Step 2: Wire create class and add student**
- Use class_service

**Step 3: Manual verification**

Run: `python -m app.main`
Expected: Teacher dashboard loads, class and student creation works

**Step 4: Commit**

```bash
git add app/ui/teacher_dashboard.py app/main.py
git commit -m "feat: add teacher dashboard shell"
```

---

### Task 9: Student dashboard basics

**Files:**
- Create: `app/ui/student_dashboard.py`
- Modify: `app/main.py`

**Step 1: Build Student dashboard layout**
- Team selector
- Roadmap builder Treeview
- Task list and update log

**Step 2: Manual verification**

Run: `python -m app.main`
Expected: Student dashboard loads with roadmap builder UI

**Step 3: Commit**

```bash
git add app/ui/student_dashboard.py app/main.py
git commit -m "feat: add student dashboard shell"
```

---

### Task 10: Roadmap builder actions

**Files:**
- Modify: `app/ui/student_dashboard.py`
- Modify: `app/services/roadmap_service.py`

**Step 1: Add phase/task create and edit actions**
- Use Treeview to add phases and tasks
- Store to DB through roadmap_service

**Step 2: Add submit action with validation**
- Call validate_roadmap
- Show warnings for weight mismatch

**Step 3: Manual verification**

Run: `python -m app.main`
Expected: Roadmap creation works and submit enforces validation

**Step 4: Commit**

```bash
git add app/ui/student_dashboard.py app/services/roadmap_service.py
git commit -m "feat: add roadmap builder actions"
```

---

### Task 11: Task execution and updates

**Files:**
- Modify: `app/ui/student_dashboard.py`
- Create: `app/services/task_service.py`

**Step 1: Add task status updates**
- Only allow if roadmap is Approved

**Step 2: Add update log entries**

**Step 3: Manual verification**

Run: `python -m app.main`
Expected: Task status updates and logs recorded

**Step 4: Commit**

```bash
git add app/ui/student_dashboard.py app/services/task_service.py
git commit -m "feat: add task execution and update logs"
```

---

### Task 12: Charts (Gantt + Burndown)

**Files:**
- Create: `app/ui/charts.py`
- Modify: `app/ui/student_dashboard.py`
- Modify: `app/ui/teacher_dashboard.py`

**Step 1: Implement chart data helpers**
- Gantt: phase/task timeline from tasks
- Burndown: total weight vs. completed weight

**Step 2: Embed Matplotlib canvas in dashboards**

**Step 3: Manual verification**

Run: `python -m app.main`
Expected: Charts render without errors

**Step 4: Commit**

```bash
git add app/ui/charts.py app/ui/student_dashboard.py app/ui/teacher_dashboard.py
git commit -m "feat: add gantt and burndown charts"
```

---

### Task 13: Final polish and smoke test

**Files:**
- Modify: `README.md`

**Step 1: Add run instructions**

**Step 2: Manual smoke test**
- Create class
- Add students
- Create team
- Draft roadmap
- Submit, approve
- Update tasks
- View charts

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add run instructions"
```
