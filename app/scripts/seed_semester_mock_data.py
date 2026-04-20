from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# Ensure local package imports work from any cwd.
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
for path in (APP_ROOT, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from core.db.connector import DBConnector
from core.db.schema import init_db
from core.services import ServiceFactory
from libs.logger import get_logger


TEAM_MIN_SIZE = 4
DEFAULT_PASSWORD = "MockData2026!"
DEFAULT_CSV_PATH = Path("/tmp/data-mock.csv")
DEFAULT_JSON_DIR = APP_ROOT / "assets" / "mock_data"
DEFAULT_REPORT_PATH = DEFAULT_JSON_DIR / "seed_report.md"
DEFAULT_CREDENTIALS_PATH = DEFAULT_JSON_DIR / "login_credentials.json"


logger = get_logger("app.scripts.seed_semester_mock_data")


@dataclass
class StudentSeed:
    student_id: str
    name: str
    department: str
    year: int
    email: str
    user_id: int | None = None


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_name(name: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in name.strip().split())


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", ".", ascii_text).strip(".").lower()
    return slug or "student"


def _build_student_email(name: str, student_id: str) -> str:
    return f"{_slugify(name)}.{student_id[-4:]}@student.mock.edu.tr"


def _parse_students_csv(csv_path: Path) -> list[StudentSeed]:
    students: list[StudentSeed] = []
    seen_emails: set[str] = set()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        header_map = {col.strip().lower(): idx for idx, col in enumerate(header)}

        for row in reader:
            if not row:
                continue
            row = [value.strip() for value in row]
            if len(row) < 4:
                continue

            # Common dataset shape in this project:
            # header: student_id,score,student_name,department,student_year
            # rows:   student_id,student_name,department,student_year
            if len(row) == 4:
                student_id, raw_name, department, year_raw = row
            else:
                student_id = row[header_map.get("student_id", 0)]
                name_idx = header_map.get("student_name", header_map.get("score", 1))
                dept_idx = header_map.get("department", 2)
                year_idx = header_map.get("student_year", len(row) - 1)

                raw_name = row[name_idx] if 0 <= name_idx < len(row) else row[1]
                department = row[dept_idx] if 0 <= dept_idx < len(row) else row[2]
                year_raw = row[year_idx] if 0 <= year_idx < len(row) else row[-1]

            department = department.lower()
            if not student_id or not raw_name or not department or not year_raw:
                continue

            try:
                year = int(year_raw)
            except ValueError:
                continue

            name = _normalize_name(raw_name)
            email = _build_student_email(name, student_id)

            # Enforce deterministic uniqueness for rare collisions.
            counter = 1
            unique_email = email
            while unique_email in seen_emails:
                unique_email = email.replace("@", f".{counter}@")
                counter += 1
            seen_emails.add(unique_email)

            students.append(
                StudentSeed(
                    student_id=student_id,
                    name=name,
                    department=department,
                    year=year,
                    email=unique_email,
                )
            )
    students.sort(key=lambda s: s.student_id)
    return students


def _load_students_json(students_json: Path) -> list[StudentSeed]:
    payload = _load_json(students_json)
    if not isinstance(payload, list):
        raise ValueError(f"Expected list in {students_json}")
    students: list[StudentSeed] = []
    for row in payload:
        students.append(
            StudentSeed(
                student_id=str(row["student_id"]),
                name=str(row["name"]),
                department=str(row["department"]).lower(),
                year=int(row["year"]),
                email=str(row["email"]),
            )
        )
    students.sort(key=lambda s: s.student_id)
    return students


def _count_existing_users(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute("SELECT COUNT(*) FROM users")
        row = cur.fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def _resolve_team_sizes(total_students: int) -> list[int]:
    if total_students < TEAM_MIN_SIZE:
        raise ValueError(
            f"Cannot build teams: total_students={total_students} < {TEAM_MIN_SIZE}"
        )

    # Build as many teams as possible while keeping each team >= TEAM_MIN_SIZE.
    team_count = total_students // TEAM_MIN_SIZE
    base = total_students // team_count
    rem = total_students % team_count
    return [base + 1] * rem + [base] * (team_count - rem)


def _chunk_by_sizes(students: list[StudentSeed], sizes: list[int]) -> list[list[StudentSeed]]:
    chunks: list[list[StudentSeed]] = []
    cursor = 0
    for size in sizes:
        chunks.append(students[cursor : cursor + size])
        cursor += size
    return chunks


def _matches_class(student: StudentSeed, class_spec: dict[str, Any]) -> bool:
    department = str(class_spec.get("department", "")).strip().lower()
    if department and student.department != department:
        return False
    year_min = class_spec.get("year_min")
    if year_min is not None and student.year < int(year_min):
        return False
    year_max = class_spec.get("year_max")
    if year_max is not None and student.year > int(year_max):
        return False
    return True


def _assign_students_to_classes(
    students: list[StudentSeed], class_specs: list[dict[str, Any]]
) -> dict[str, list[StudentSeed]]:
    by_code: dict[str, list[StudentSeed]] = {str(c["code"]): [] for c in class_specs}
    cse_codes = [
        str(c["code"])
        for c in class_specs
        if str(c.get("department", "")).lower() == "cse"
    ]
    bme_codes = [
        str(c["code"])
        for c in class_specs
        if str(c.get("department", "")).lower() == "bme"
    ]

    for student in students:
        matches = [c for c in class_specs if _matches_class(student, c)]
        if len(matches) == 1:
            by_code[str(matches[0]["code"])].append(student)
            continue
        if len(matches) > 1:
            # Prefer tighter constraints (year filters) when multiple match.
            matches.sort(
                key=lambda c: (
                    0 if c.get("year_min") is not None or c.get("year_max") is not None else 1
                )
            )
            by_code[str(matches[0]["code"])].append(student)
            continue

        # Fallback routing when no strict match is found.
        if student.department == "cse" and cse_codes:
            target = min(cse_codes, key=lambda code: len(by_code[code]))
            by_code[target].append(student)
            continue
        if student.department == "bme" and bme_codes:
            target = min(bme_codes, key=lambda code: len(by_code[code]))
            by_code[target].append(student)
            continue
        raise ValueError(f"No class mapping found for student {student.student_id}")

    for code, bucket in by_code.items():
        bucket.sort(key=lambda s: s.student_id)
        if len(bucket) < TEAM_MIN_SIZE:
            raise ValueError(
                f"Class {code} has {len(bucket)} students, fewer than minimum "
                f"{TEAM_MIN_SIZE} required to create a team."
            )
    return by_code


def _format_title(template: str, project: str) -> str:
    return template.format(project=project).strip()


SCENARIO_ORDER = (
    "finished",
    "not_started",
    "linear_progress",
    "improving_productivity",
)

SCENARIO_LABELS = {
    "finished": "Finished",
    "not_started": "Not Started",
    "linear_progress": "Linear Progress",
    "improving_productivity": "Improving Productivity",
}


def _scenario_for_team_index(global_team_index: int) -> str:
    return SCENARIO_ORDER[(global_team_index - 1) % len(SCENARIO_ORDER)]


def _task_completion_plan(task_count: int, scenario: str) -> tuple[int, int]:
    if task_count <= 0:
        return 0, 0
    if scenario == "finished":
        return task_count, 0
    if scenario == "not_started":
        return 0, 0
    if scenario == "linear_progress":
        done = max(1, task_count // 3)
        in_progress = 1 if done < task_count else 0
        return done, in_progress
    # improving_productivity
    done = max(1, (task_count * 2) // 3)
    in_progress = 1 if done < task_count else 0
    return done, in_progress


def _scenario_percent_timeline(scenario: str) -> list[int]:
    if scenario == "finished":
        return [35, 70, 100]
    if scenario == "not_started":
        return [0, 0, 5]
    if scenario == "linear_progress":
        return [15, 30, 45]
    return [10, 25, 55]  # improving_productivity


def _scenario_checkin_status(scenario: str, week_index: int) -> str:
    if scenario == "finished":
        return ["On Track", "On Track", "Approved"][week_index]
    if scenario == "not_started":
        return ["Needs Attention", "Needs Attention", "At Risk"][week_index]
    if scenario == "linear_progress":
        return ["On Track", "On Track", "On Track"][week_index]
    return ["Needs Attention", "On Track", "On Track"][week_index]


def _scenario_wins_text(scenario: str, project: str, week_index: int) -> str:
    if scenario == "finished":
        return [
            f"{project}: requirements and architecture finalized.",
            f"{project}: implementation milestones completed on schedule.",
            f"{project}: validation and handoff package completed.",
        ][week_index]
    if scenario == "not_started":
        return [
            f"{project}: team assignment and roles clarified.",
            f"{project}: kickoff meeting held with class mentor.",
            f"{project}: scope clarified, start blocked by preparation tasks.",
        ][week_index]
    if scenario == "linear_progress":
        return [
            f"{project}: first implementation tasks completed.",
            f"{project}: steady progress with consistent delivery cadence.",
            f"{project}: another phase completed with expected throughput.",
        ][week_index]
    return [
        f"{project}: team recovered from a slow kickoff.",
        f"{project}: delivery speed improved after process adjustments.",
        f"{project}: productivity trend is up and phase completion accelerated.",
    ][week_index]


def _scenario_risks_text(scenario: str, week_index: int) -> str:
    if scenario == "finished":
        return [
            "Minor documentation debt.",
            "Regression risk during final merge.",
            "No major risk; monitoring release quality.",
        ][week_index]
    if scenario == "not_started":
        return [
            "Unclear implementation ownership.",
            "Delayed environment setup.",
            "Timeline slip risk if execution does not begin this week.",
        ][week_index]
    if scenario == "linear_progress":
        return [
            "Dependency coordination needed across teammates.",
            "Review queue can slow completion rate.",
            "Quality checks must keep pace with delivery.",
        ][week_index]
    return [
        "Initial planning quality was low.",
        "Increased delivery speed may introduce rework.",
        "Need to sustain pace without quality drop.",
    ][week_index]


def _scenario_next_goal_text(scenario: str, project: str, week_index: int) -> str:
    if scenario == "finished":
        return [
            f"Complete implementation for {project}.",
            f"Finish remaining QA activities for {project}.",
            f"Archive roadmap and share retrospective for {project}.",
        ][week_index]
    if scenario == "not_started":
        return [
            f"Start first phase implementation for {project}.",
            f"Move at least one task to in-progress.",
            f"Deliver first completed task and stabilize cadence.",
        ][week_index]
    if scenario == "linear_progress":
        return [
            f"Maintain weekly throughput for {project}.",
            f"Complete next phase with the same cadence.",
            f"Close open tasks and prepare integration checks.",
        ][week_index]
    return [
        f"Stabilize improved workflow on {project}.",
        f"Convert in-progress tasks to done faster than prior week.",
        f"Lock in velocity gains and finalize remaining tasks.",
    ][week_index]


def _scenario_help_needed(scenario: str, week_index: int) -> str | None:
    if scenario == "finished":
        return None if week_index == 2 else "Final review feedback from teacher."
    if scenario == "not_started":
        return "Guidance on prioritizing startup tasks and execution plan."
    if scenario == "linear_progress":
        return "Occasional review support on intermediate deliverables."
    return "Support on quality gates while throughput is increasing."


def _metrics_from_percent(total_weight: int, percent: int) -> dict[str, int]:
    percent_clamped = max(0, min(100, percent))
    done = int(round((total_weight * percent_clamped) / 100)) if total_weight else 0
    done = max(0, min(total_weight, done))
    return {"total": total_weight, "done": done, "percent": percent_clamped}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _log_banner(title: str) -> None:
    logger.banner(title, width=78, char="═")


def _build_credentials_payload(
    teacher_accounts: dict[str, Any], students: list[StudentSeed]
) -> dict[str, Any]:
    teachers = [
        {
            "name": account.name,
            "email": account.email,
            "password": DEFAULT_PASSWORD,
        }
        for account in teacher_accounts.values()
    ]
    teachers.sort(key=lambda row: row["email"])

    student_accounts = [
        {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "password": DEFAULT_PASSWORD,
        }
        for student in students
    ]
    student_accounts.sort(key=lambda row: row["student_id"])

    quick_teacher = teachers[0] if teachers else None
    quick_student = student_accounts[0] if student_accounts else None

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "password_note": "All generated mock users use the same password.",
        "default_password": DEFAULT_PASSWORD,
        "quick_login": {
            "teacher": quick_teacher,
            "student": quick_student,
        },
        "teachers": teachers,
        "students": student_accounts,
    }


def _render_final_report(
    db_path: Path,
    csv_path: Path,
    summary: dict[str, Any],
    credentials: dict[str, Any],
    summary_json_path: Path,
    credentials_json_path: Path,
) -> str:
    totals = summary.get("totals", {})
    scenario_totals = summary.get("scenario_totals", {})
    quick_login = credentials.get("quick_login", {})
    quick_teacher = quick_login.get("teacher") or {}
    quick_student = quick_login.get("student") or {}
    classes = summary.get("classes", [])

    lines: list[str] = []
    lines.append("# Mock Data Seed Final Report")
    lines.append("")
    lines.append(f"- Generated at: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Database: `{db_path}`")
    lines.append(f"- Source CSV: `{csv_path}`")
    lines.append(f"- Summary JSON: `{summary_json_path}`")
    lines.append(f"- Credentials JSON: `{credentials_json_path}`")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append(f"- Teachers: **{totals.get('teachers', 0)}**")
    lines.append(f"- Students: **{totals.get('students', 0)}**")
    lines.append(f"- Teams: **{totals.get('teams', 0)}**")
    lines.append(f"- Roadmaps: **{totals.get('roadmaps', 0)}**")
    lines.append(f"- Tasks: **{totals.get('tasks', 0)}**")
    lines.append(f"- Check-ins: **{totals.get('checkins', 0)}**")
    lines.append("")
    lines.append("## Scenario Coverage")
    lines.append("")
    lines.append("| Scenario | Teams |")
    lines.append("| --- | ---: |")
    for scenario in (
        "Finished",
        "Not Started",
        "Linear Progress",
        "Improving Productivity",
    ):
        lines.append(f"| {scenario} | {int(scenario_totals.get(scenario, 0))} |")
    lines.append("")
    lines.append("## Quick Login")
    lines.append("")
    lines.append("Use these credentials to sign in immediately:")
    lines.append("")
    lines.append(f"- Teacher email: `{quick_teacher.get('email', 'N/A')}`")
    lines.append(f"- Teacher password: `{quick_teacher.get('password', DEFAULT_PASSWORD)}`")
    lines.append(f"- Student email: `{quick_student.get('email', 'N/A')}`")
    lines.append(f"- Student password: `{quick_student.get('password', DEFAULT_PASSWORD)}`")
    lines.append("")
    lines.append("## Teacher Accounts")
    lines.append("")
    lines.append("| Name | Email | Password |")
    lines.append("| --- | --- | --- |")
    for teacher in credentials.get("teachers", []):
        lines.append(
            f"| {teacher['name']} | `{teacher['email']}` | `{teacher['password']}` |"
        )
    lines.append("")
    lines.append("## Classes")
    lines.append("")
    lines.append("| Code | Name | Teacher | Students | Teams |")
    lines.append("| --- | --- | --- | ---: | ---: |")
    for class_row in classes:
        lines.append(
            f"| {class_row['code']} | {class_row['name']} | {class_row['teacher']} "
            f"| {class_row['student_count']} | {class_row['team_count']} |"
        )
    lines.append("")
    lines.append("## Student Credentials")
    lines.append("")
    lines.append(
        f"Full student credentials are saved in `{credentials_json_path}` "
        "(includes email + password for each student)."
    )
    lines.append("")
    return "\n".join(lines)


def seed_dataset(
    db_path: Path,
    csv_path: Path,
    json_dir: Path,
    students_json_path: Path,
    summary_json_path: Path,
    report_path: Path,
    credentials_json_path: Path,
    reset: bool,
) -> None:
    _log_banner("Mock Data Seeding Started")
    logger.info("Database target     : %s", db_path)
    logger.info("Input CSV           : %s", csv_path)
    logger.info("JSON config dir     : %s", json_dir)
    logger.info("Reset enabled       : %s", "yes" if reset else "no")

    teachers_path = json_dir / "teachers.json"
    classes_path = json_dir / "classes.json"
    projects_path = json_dir / "projects.json"
    roadmap_templates_path = json_dir / "roadmap_templates.json"

    teachers = _load_json(teachers_path)
    class_specs = _load_json(classes_path)
    projects = _load_json(projects_path)
    roadmap_templates = _load_json(roadmap_templates_path)
    logger.info(
        "Loaded configs      : teachers=%d classes=%d projects=%d",
        len(teachers) if isinstance(teachers, list) else 0,
        len(class_specs) if isinstance(class_specs, list) else 0,
        len(projects) if isinstance(projects, list) else 0,
    )

    if not isinstance(teachers, list) or not teachers:
        raise ValueError("teachers.json must contain a non-empty list")
    if not isinstance(class_specs, list) or not class_specs:
        raise ValueError("classes.json must contain a non-empty list")
    if not isinstance(projects, list) or not projects:
        raise ValueError("projects.json must contain a non-empty list")
    if not isinstance(roadmap_templates, dict) or "phases" not in roadmap_templates:
        raise ValueError("roadmap_templates.json must contain {\"phases\": [...]}")

    if reset and db_path.exists():
        logger.info("Deleting existing DB: %s", db_path)
        db_path.unlink()
    if not reset and _count_existing_users(db_path) > 0:
        raise ValueError(
            "Database already contains users. Re-run with --reset to reseed safely."
        )

    if csv_path.exists():
        students = _parse_students_csv(csv_path)
        logger.info("Loaded students     : %d (from CSV)", len(students))
    elif students_json_path.exists():
        students = _load_students_json(students_json_path)
        logger.info("Loaded students     : %d (from JSON)", len(students))
    else:
        raise FileNotFoundError(
            f"Neither CSV nor students JSON found: {csv_path} / {students_json_path}"
        )

    if not students:
        raise ValueError("No students loaded from CSV/JSON")

    _write_json(students_json_path, [asdict(s) for s in students])
    logger.info("Wrote students JSON : %s", students_json_path)

    init_db(str(db_path))
    services = ServiceFactory(DBConnector(str(db_path)))
    services.app_state_service.set_dataset_mode("mock")
    logger.info("Database initialized and dataset mode set to mock")

    teacher_accounts: dict[str, Any] = {}
    for teacher in teachers:
        account = services.auth_service.sign_up(
            str(teacher["name"]).strip(),
            str(teacher["email"]).strip().lower(),
            DEFAULT_PASSWORD,
            "teacher",
        )
        teacher_accounts[account.email] = account
    logger.info("Created teachers    : %d", len(teacher_accounts))

    class_meta: dict[str, dict[str, Any]] = {}
    for class_spec in class_specs:
        teacher_email = str(class_spec["teacher_email"]).strip().lower()
        if teacher_email not in teacher_accounts:
            raise ValueError(f"Teacher not found for class: {teacher_email}")
        owner = teacher_accounts[teacher_email]
        class_id = services.class_service.create_class(
            str(class_spec["name"]).strip(),
            str(class_spec["term"]).strip(),
            owner_user_id=owner.id,
        )
        code = str(class_spec["code"]).strip()
        class_meta[code] = {
            "id": class_id,
            "teacher_name": owner.name,
            "teacher_email": owner.email,
            "name": str(class_spec["name"]).strip(),
        }
    logger.info("Created classes     : %d", len(class_meta))

    for student in students:
        account = services.auth_service.sign_up(
            student.name,
            student.email,
            DEFAULT_PASSWORD,
            "student",
        )
        student.user_id = account.id
    logger.info("Created students    : %d", len(students))

    students_by_class = _assign_students_to_classes(students, class_specs)
    for code, assigned in students_by_class.items():
        logger.info("Class assignment    : %s -> %d students", code, len(assigned))

    phases = roadmap_templates["phases"]
    global_project_idx = 0
    global_team_idx = 0
    summary: dict[str, Any] = {
        "classes": [],
        "scenario_totals": {label: 0 for label in SCENARIO_LABELS.values()},
        "totals": {
            "teachers": len(teacher_accounts),
            "students": len(students),
            "teams": 0,
            "roadmaps": 0,
            "tasks": 0,
            "checkins": 0,
        },
    }

    for class_spec in class_specs:
        code = str(class_spec["code"]).strip()
        class_students = students_by_class[code]
        team_sizes = _resolve_team_sizes(len(class_students))
        team_memberships = _chunk_by_sizes(class_students, team_sizes)
        class_summary = {
            "code": code,
            "name": class_meta[code]["name"],
            "teacher": class_meta[code]["teacher_name"],
            "student_count": len(class_students),
            "team_count": len(team_memberships),
            "teams": [],
        }
        logger.info(
            "Team planning       : %s -> %d teams (students=%d)",
            code,
            len(team_memberships),
            len(class_students),
        )

        for team_index, members in enumerate(team_memberships, start=1):
            global_team_idx += 1
            project = str(projects[global_project_idx % len(projects)]).strip()
            global_project_idx += 1
            team_name = f"{code}-Team-{team_index:02d}"
            scenario_key = _scenario_for_team_index(global_team_idx)
            scenario_label = SCENARIO_LABELS[scenario_key]

            principal = members[0]
            if principal.user_id is None:
                raise ValueError(f"Missing user id for principal {principal.student_id}")

            team_id = services.team_service.create_team(
                class_meta[code]["id"], team_name, principal.user_id
            )
            services.team_service.update_team_principal(team_id, principal.user_id)

            for member in members:
                if member.user_id is None:
                    raise ValueError(f"Missing user id for member {member.student_id}")
                services.team_service.add_team_member(team_id, member.user_id)

            roadmap_id = services.roadmap_service.create_roadmap(team_id)
            created_task_ids: list[int] = []
            task_weights: list[int] = []

            for phase_index, phase in enumerate(phases, start=1):
                phase_name = _format_title(str(phase["name"]), project)
                phase_id = services.roadmap_service.create_phase(
                    roadmap_id, phase_name, phase_index
                )
                for task_index, task in enumerate(phase["tasks"], start=1):
                    assignee = members[(task_index - 1) % len(members)]
                    if assignee.user_id is None:
                        raise ValueError(
                            f"Missing user id for assignee {assignee.student_id}"
                        )
                    title = _format_title(str(task["title"]), project)
                    weight = int(task.get("weight", 8))
                    task_id = services.roadmap_service.create_task(
                        phase_id,
                        title,
                        weight,
                        assignee_user_id=assignee.user_id,
                    )
                    created_task_ids.append(task_id)
                    task_weights.append(weight)

            done_count, in_progress_count = _task_completion_plan(
                len(created_task_ids), scenario_key
            )
            done_task_ids = created_task_ids[:done_count]
            in_progress_task_ids = created_task_ids[
                done_count : done_count + in_progress_count
            ]

            for idx, task_id in enumerate(done_task_ids, start=1):
                member = members[(idx - 1) % len(members)]
                services.task_service.update_task_status(task_id, "Done")
                done_note = {
                    "finished": f"{project} deliverable #{idx} completed and documented.",
                    "linear_progress": f"{project} task #{idx} completed as planned.",
                    "improving_productivity": (
                        f"{project} task #{idx} completed faster than prior sprint."
                    ),
                    "not_started": f"{project} task #{idx} completed.",
                }[scenario_key]
                services.task_service.add_update(
                    task_id,
                    member.user_id or 0,
                    done_note,
                )

            for idx, task_id in enumerate(in_progress_task_ids, start=1):
                member = members[(done_count + idx - 1) % len(members)]
                services.task_service.update_task_status(
                    task_id, "In Progress"
                )
                in_progress_note = {
                    "linear_progress": (
                        f"{project} implementation is moving steadily with expected velocity."
                    ),
                    "improving_productivity": (
                        f"{project} execution picked up this week after process tuning."
                    ),
                    "finished": f"{project} wrap-up task is in final review.",
                    "not_started": f"{project} kickoff task moved to in progress.",
                }[scenario_key]
                services.task_service.add_update(
                    task_id,
                    member.user_id or 0,
                    in_progress_note,
                )

            if scenario_key in {"finished", "linear_progress", "improving_productivity"}:
                services.roadmap_service.submit_roadmap(roadmap_id)
            if scenario_key == "finished":
                services.roadmap_service.approve_roadmap(roadmap_id)
            roadmap_status = services.roadmap_service.get_roadmap_status(roadmap_id)

            services.roadmap_service.add_roadmap_comment(
                roadmap_id=roadmap_id,
                author=class_meta[code]["teacher_name"],
                text=(
                    f"Project '{project}' seeded with scenario '{scenario_label}' "
                    f"for {team_name}."
                ),
                kind="comment",
            )

            total_weight = sum(task_weights)
            percent_timeline = _scenario_percent_timeline(scenario_key)
            team_start_week = date(2026, 2, 10) + timedelta(days=7 * (global_team_idx - 1))
            checkin_ids: list[int] = []
            for week_index, percent in enumerate(percent_timeline):
                week_start_date = team_start_week + timedelta(days=7 * week_index)
                week_end_date = week_start_date + timedelta(days=6)
                checkin_status = _scenario_checkin_status(scenario_key, week_index)
                metrics = _metrics_from_percent(total_weight, percent)
                checkin_id = services.checkin_service.create_checkin(
                    team_id=team_id,
                    week_start=week_start_date.isoformat(),
                    week_end=week_end_date.isoformat(),
                    status=checkin_status,
                    wins=_scenario_wins_text(scenario_key, project, week_index),
                    risks=_scenario_risks_text(scenario_key, week_index),
                    next_goal=_scenario_next_goal_text(scenario_key, project, week_index),
                    help_needed=_scenario_help_needed(scenario_key, week_index),
                    metrics=metrics,
                )
                comment = (
                    f"Scenario={scenario_label}. "
                    f"Week {week_index + 1}: monitor plan adherence and quality."
                )
                if scenario_key == "improving_productivity" and week_index == 2:
                    comment = (
                        "Scenario=Improving Productivity. "
                        "Velocity increased significantly; keep QA discipline high."
                    )
                if scenario_key == "not_started" and week_index == 2:
                    comment = (
                        "Scenario=Not Started. "
                        "Escalate blockers and align immediate execution plan."
                    )
                services.checkin_service.add_checkin_comment(
                    checkin_id=checkin_id,
                    author=class_meta[code]["teacher_name"],
                    text=comment,
                    kind="comment",
                )
                checkin_ids.append(checkin_id)

            if scenario_key == "finished" and checkin_ids:
                services.checkin_service.approve_checkin(checkin_ids[-1])

            class_summary["teams"].append(
                {
                    "team_name": team_name,
                    "project": project,
                    "scenario": scenario_label,
                    "size": len(members),
                    "principal_student_id": principal.student_id,
                    "roadmap_id": roadmap_id,
                    "roadmap_status": roadmap_status,
                    "checkin_id": checkin_ids[-1] if checkin_ids else None,
                    "checkin_count": len(checkin_ids),
                    "progress_percent": percent_timeline[-1],
                }
            )
            summary["totals"]["teams"] += 1
            summary["totals"]["roadmaps"] += 1
            summary["totals"]["tasks"] += len(created_task_ids)
            summary["totals"]["checkins"] += len(checkin_ids)
            summary["scenario_totals"][scenario_label] += 1

        summary["classes"].append(class_summary)

    credentials_payload = _build_credentials_payload(teacher_accounts, students)
    summary["credentials"] = {
        "default_password": credentials_payload["default_password"],
        "credentials_json": str(credentials_json_path),
        "quick_login": credentials_payload["quick_login"],
    }

    _write_json(summary_json_path, summary)
    _write_json(credentials_json_path, credentials_payload)
    final_report = _render_final_report(
        db_path=db_path,
        csv_path=csv_path,
        summary=summary,
        credentials=credentials_payload,
        summary_json_path=summary_json_path,
        credentials_json_path=credentials_json_path,
    )
    _write_text(report_path, final_report)

    totals = summary["totals"]
    logger.info(
        "Seeding complete    : teachers=%d students=%d teams=%d roadmaps=%d tasks=%d checkins=%d",
        totals["teachers"],
        totals["students"],
        totals["teams"],
        totals["roadmaps"],
        totals["tasks"],
        totals["checkins"],
    )
    _log_banner("Mock Data Seeding Finished")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed the app database from JSON mock config + Turkish students CSV."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=APP_ROOT / "app.db",
        help="SQLite path (default: app/app.db)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help="CSV source for students (default: /tmp/data-mock.csv)",
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=DEFAULT_JSON_DIR,
        help="Directory containing classes/teachers/projects/templates JSON files",
    )
    parser.add_argument(
        "--students-json",
        type=Path,
        default=DEFAULT_JSON_DIR / "students.json",
        help="Path to write/read normalized students JSON",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=DEFAULT_JSON_DIR / "seed_summary.json",
        help="Path to write seeding summary JSON",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to write final markdown report",
    )
    parser.add_argument(
        "--credentials-json",
        type=Path,
        default=DEFAULT_CREDENTIALS_PATH,
        help="Path to write credential list JSON",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing DB file before seeding",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_dataset(
        db_path=args.db,
        csv_path=args.csv,
        json_dir=args.json_dir,
        students_json_path=args.students_json,
        summary_json_path=args.summary_json,
        report_path=args.report,
        credentials_json_path=args.credentials_json,
        reset=args.reset,
    )
    logger.success("Seeded mock dataset into %s", args.db)
    logger.info("Students JSON: %s", args.students_json)
    logger.info("Summary JSON: %s", args.summary_json)
    logger.info("Credentials JSON: %s", args.credentials_json)
    logger.info("Final Report: %s", args.report)

    credentials = _load_json(args.credentials_json)
    quick = credentials.get("quick_login", {})
    teacher = quick.get("teacher", {})
    student = quick.get("student", {})
    logger.banner("Quick Login")
    logger.success(
        "Teacher -> %s / %s",
        teacher.get("email", "N/A"),
        teacher.get("password", DEFAULT_PASSWORD),
    )
    logger.success(
        "Student -> %s / %s",
        student.get("email", "N/A"),
        student.get("password", DEFAULT_PASSWORD),
    )


if __name__ == "__main__":
    main()
