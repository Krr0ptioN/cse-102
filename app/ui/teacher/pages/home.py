from __future__ import annotations

import tkinter as tk

from app.ui.components.ui import Section


class TeacherHomePage(tk.Frame):
    """Dashboard analytics / snapshots for the teacher."""

    title = "Dashboard"

    def __init__(self, master, services: dict, class_id: int | None) -> None:
        colors_bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=colors_bg)
        self.services = services
        self.class_id = class_id

        self._build()
        self._refresh()

    def _build(self) -> None:
        top = tk.Frame(self, bg=self["bg"])
        top.pack(fill="x", padx=10, pady=10)

        self.stats_section = Section(
            top, "Overview", subtitle="Snapshot for this class"
        )
        self.stats_section.pack(fill="x", padx=4, pady=4)
        stats_body = tk.Frame(self.stats_section.body, bg=self.stats_section.body["bg"])
        stats_body.pack(fill="x", pady=4)
        stats_body.columnconfigure(0, weight=1)
        stats_body.columnconfigure(1, weight=1)
        stats_body.columnconfigure(2, weight=1)

        self.lbl_students = tk.Label(
            stats_body, text="Students: 0", bg=stats_body["bg"], anchor="w"
        )
        self.lbl_students.grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.lbl_teams = tk.Label(
            stats_body, text="Teams: 0", bg=stats_body["bg"], anchor="w"
        )
        self.lbl_teams.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.lbl_roadmaps = tk.Label(
            stats_body, text="Roadmaps: 0", bg=stats_body["bg"], anchor="w"
        )
        self.lbl_roadmaps.grid(row=0, column=2, sticky="w", padx=6, pady=4)

        mid = tk.Frame(self, bg=self["bg"])
        mid.pack(fill="both", expand=True, padx=10, pady=6)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        self.recent_checkins = Section(mid, "Recent Check-ins")
        self.recent_checkins.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.checkin_list = tk.Listbox(
            self.recent_checkins.body,
            height=8,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
        )
        self.checkin_list.pack(fill="both", expand=True, padx=6, pady=6)

        self.recent_roadmaps = Section(mid, "Recent Roadmaps")
        self.recent_roadmaps.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self.roadmap_list = tk.Listbox(
            self.recent_roadmaps.body,
            height=8,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
        )
        self.roadmap_list.pack(fill="both", expand=True, padx=6, pady=6)

    def _refresh(self) -> None:
        if not self.class_id:
            return
        class_svc = self.services["class"]
        team_svc = self.services["team"]
        roadmap_svc = self.services["roadmap"]
        checkin_svc = self.services["checkin"]

        students = class_svc.list_users(role="student")
        teams = team_svc.list_teams(self.class_id)
        roadmaps = roadmap_svc.list_roadmaps_for_class(self.class_id)
        self.lbl_students.config(text=f"Students: {len(students)}")
        self.lbl_teams.config(text=f"Teams: {len(teams)}")
        self.lbl_roadmaps.config(text=f"Roadmaps: {len(roadmaps)}")

        # Recent check-ins
        self.checkin_list.delete(0, tk.END)
        recent_checkins = checkin_svc.list_checkins_for_class(self.class_id)[:5]
        for c in recent_checkins:
            self.checkin_list.insert(
                tk.END,
                f"#{c['id']} {c['team']} {c['status']} {c['week_start']}→{c['week_end']} ({c['percent']}%)",
            )

        # Recent roadmaps
        self.roadmap_list.delete(0, tk.END)
        for r in roadmaps[:5]:
            principal = r.get("principal") or "-"
            self.roadmap_list.insert(
                tk.END, f"#{r['id']} {r['team']} · {principal} · {r['status']}"
            )
