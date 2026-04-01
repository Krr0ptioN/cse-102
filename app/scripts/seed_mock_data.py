from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app.*` works when run from app/.
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.db.connector import DBConnector
from app.db.schema import init_db
from app.services.factory import ServiceFactory


DEMO_PASSWORD = "demo1234"
DEMO_TEACHER_NAME = "Demo Teacher"
DEMO_TEACHER_EMAIL = "teacher.demo@example.edu"


def seed(db_path: Path) -> None:
    init_db(str(db_path))
    services = ServiceFactory(DBConnector(str(db_path)))
    services.app_state_service.set_dataset_mode("mock")

    teacher = services.auth_service.sign_up(
        DEMO_TEACHER_NAME,
        DEMO_TEACHER_EMAIL,
        DEMO_PASSWORD,
        "teacher",
    )

    # Create class
    class_id = services.class_service.create_class(
        "Project Lifecycle Engineering", "Spring 2026", owner_user_id=teacher.id
    )

    # Students
    students = [
        ("Ava Thompson", "ava.thompson@example.edu"),
        ("Noah Williams", "noah.williams@example.edu"),
        ("Liam Patel", "liam.patel@example.edu"),
        ("Emma Chen", "emma.chen@example.edu"),
        ("Mia Robinson", "mia.robinson@example.edu"),
        ("Ethan Brooks", "ethan.brooks@example.edu"),
        ("Sophia Garcia", "sophia.garcia@example.edu"),
        ("Oliver Davis", "oliver.davis@example.edu"),
        ("Lucas Reed", "lucas.reed@example.edu"),
        ("Grace Nguyen", "grace.nguyen@example.edu"),
    ]

    student_ids: dict[str, int] = {}
    for name, email in students:
        account = services.auth_service.sign_up(name, email, DEMO_PASSWORD, "student")
        student_ids[name] = account.id

    # Teams (English names) with principals
    team_defs = [
        {
            "name": "Atlas Innovators",
            "members": ["Ava Thompson", "Noah Williams", "Liam Patel"],
            "principal": "Ava Thompson",
        },
        {
            "name": "Northstar Builders",
            "members": ["Emma Chen", "Mia Robinson"],
            "principal": "Emma Chen",
        },
        {
            "name": "Brightpath Crew",
            "members": ["Ethan Brooks", "Sophia Garcia", "Oliver Davis"],
            "principal": "Sophia Garcia",
        },
    ]

    team_ids: dict[str, int] = {}
    team_tasks: dict[str, list[int]] = {}

    for team_def in team_defs:
        principal_id = student_ids[team_def["principal"]]
        team_id = services.team_service.create_team(
            class_id, team_def["name"], principal_id
        )
        team_ids[team_def["name"]] = team_id
        services.team_service.update_team_principal(team_id, principal_id)
        for member_name in team_def["members"]:
            services.team_service.add_team_member(team_id, student_ids[member_name])

        team_tasks[team_def["name"]] = []

    # Roadmaps, phases, tasks
    phase_names = ["Discovery", "Design", "Implementation", "Validation"]

    roadmap_text = {
        "Discovery": [
            ("Clarify problem statement", 10),
            ("Interview stakeholders", 15),
        ],
        "Design": [
            ("Draft system architecture", 15),
            ("Review architecture with mentor", 10),
        ],
        "Implementation": [
            ("Build core features", 15),
            ("Integrate data flows", 10),
            ("Add UX polish", 10),
        ],
        "Validation": [
            ("Write test plan", 5),
            ("Run functional tests", 5),
            ("Prepare demo", 5),
        ],
    }

    for team_name, team_id in team_ids.items():
        team_def = next(td for td in team_defs if td["name"] == team_name)
        roadmap_id = services.roadmap_service.create_roadmap(team_id)
        sort_order = 1
        for phase_name in phase_names:
            phase_id = services.roadmap_service.create_phase(
                roadmap_id, phase_name, sort_order
            )
            sort_order += 1
            for title, weight in roadmap_text[phase_name]:
                task_id = services.roadmap_service.create_task(phase_id, title, weight)
                team_tasks[team_name].append(task_id)
        services.roadmap_service.add_roadmap_comment(
            roadmap_id,
            author=DEMO_TEACHER_NAME,
            text=f"Roadmap for {team_name} initialized with four phases.",
            kind="comment",
        )

        # Mark some tasks progressed and add updates
        tasks_for_team = team_tasks[team_name]
        if tasks_for_team:
            services.task_service.update_task_status(tasks_for_team[0], "Done")
        if len(tasks_for_team) > 1:
            services.task_service.update_task_status(tasks_for_team[1], "In Progress")

        member_id = student_ids[team_def["members"][0]]
        if tasks_for_team:
            services.task_service.add_update(
                tasks_for_team[0], member_id, "Completed initial planning outline."
            )
        if len(tasks_for_team) > 1:
            services.task_service.add_update(
                tasks_for_team[1],
                member_id,
                "Drafted architecture diagram and shared with team.",
            )

        # Create check-in with comments
        metrics = services.checkin_service.compute_metrics(team_id)
        week_start = "2026-03-09"
        week_end = "2026-03-15"
        checkin_id = services.checkin_service.create_checkin(
            team_id,
            week_start,
            week_end,
            status="On Track",
            wins="Team aligned on scope; completed discovery tasks.",
            risks="Need clarification on API limits.",
            next_goal="Finalize design and begin implementation.",
            help_needed=None,
            metrics=metrics,
        )
        services.checkin_service.add_checkin_comment(
            checkin_id,
            DEMO_TEACHER_NAME,
            "Good momentum. Please clarify risks with mentor.",
            "comment",
        )

        # Invitations (pending/declined)
        pending_invitee = student_ids.get("Lucas Reed")
        declined_invitee = student_ids.get("Grace Nguyen")
        if pending_invitee:
            services.team_service.create_invitation(team_id, pending_invitee)
        if declined_invitee:
            inv_id = services.team_service.create_invitation(team_id, declined_invitee)
            services.team_service.decline_invitation(inv_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed mock data into app.db")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "app.db",
        help="Path to the SQLite database (default: app/app.db)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing database file before seeding",
    )
    args = parser.parse_args()
    if args.reset and args.db.exists():
        args.db.unlink()
    seed(args.db)
    print(f"Seeded mock data into {args.db}")


if __name__ == "__main__":
    main()
