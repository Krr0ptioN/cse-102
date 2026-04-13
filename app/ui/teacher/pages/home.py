from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import Button, Card, DataTable, Input, SectionHeader, StatCard


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
        top.pack(fill="x", padx=10, pady=(10, 4))

        self.stats_card = Card(top)
        self.stats_card.pack(fill="x", padx=4, pady=4)
        SectionHeader(
            self.stats_card,
            title="Overview",
            subtitle="Snapshot for this class",
        ).pack(fill="x", padx=10, pady=(8, 2))

        stats_body = tk.Frame(self.stats_card, bg=self.stats_card["bg"])
        stats_body.pack(fill="x", padx=10, pady=(0, 10))
        self._stats = {
            "Students": StatCard(stats_body, "Students", "0"),
            "Teams": StatCard(stats_body, "Teams", "0"),
            "Roadmaps": StatCard(stats_body, "Roadmaps", "0"),
        }
        for card in self._stats.values():
            card.pack(side="left", fill="x", expand=True, padx=6, pady=4)

        mid = tk.Frame(self, bg=self["bg"])
        mid.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        checkins_card = Card(mid)
        checkins_card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        SectionHeader(checkins_card, title="Recent Check-ins").pack(
            fill="x", padx=10, pady=(8, 2)
        )
        self.checkins_filter_var = tk.StringVar(value="")
        checkins_filter_row = tk.Frame(checkins_card, bg=checkins_card["bg"])
        checkins_filter_row.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(checkins_filter_row, text="Filter", bg=checkins_card["bg"]).pack(
            side="left"
        )
        self.checkins_filter_entry = Input(
            checkins_filter_row,
            width=24,
            textvariable=self.checkins_filter_var,
        )
        self.checkins_filter_entry.pack(side="left", padx=(8, 8))
        self.checkins_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_checkins_filter(),
        )
        Button(
            checkins_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_checkins_filter,
        ).pack(side="left")

        self.checkins_table = DataTable(
            checkins_card,
            ["ID", "Team", "Status", "Week", "%"],
            height=8,
        )
        self.checkins_table.pack(fill="both", expand=True, padx=10, pady=(2, 10))

        roadmaps_card = Card(mid)
        roadmaps_card.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        SectionHeader(roadmaps_card, title="Recent Roadmaps").pack(
            fill="x", padx=10, pady=(8, 2)
        )
        self.roadmaps_filter_var = tk.StringVar(value="")
        roadmaps_filter_row = tk.Frame(roadmaps_card, bg=roadmaps_card["bg"])
        roadmaps_filter_row.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(roadmaps_filter_row, text="Filter", bg=roadmaps_card["bg"]).pack(
            side="left"
        )
        self.roadmaps_filter_entry = Input(
            roadmaps_filter_row,
            width=24,
            textvariable=self.roadmaps_filter_var,
        )
        self.roadmaps_filter_entry.pack(side="left", padx=(8, 8))
        self.roadmaps_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_roadmaps_filter(),
        )
        Button(
            roadmaps_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_roadmaps_filter,
        ).pack(side="left")

        self.roadmaps_table = DataTable(
            roadmaps_card,
            ["ID", "Team", "Principal", "Status"],
            height=8,
        )
        self.roadmaps_table.pack(fill="both", expand=True, padx=10, pady=(2, 10))

    def _refresh(self) -> None:
        if not self.class_id:
            self._stats["Students"].set_value("0")
            self._stats["Teams"].set_value("0")
            self._stats["Roadmaps"].set_value("0")
            self.checkins_table.set_rows([])
            self.roadmaps_table.set_rows([])
            self._apply_checkins_filter()
            self._apply_roadmaps_filter()
            return
        class_svc = self.services["class"]
        team_svc = self.services["team"]
        roadmap_svc = self.services["roadmap"]
        checkin_svc = self.services["checkin"]

        students = class_svc.list_users(role="student")
        teams = team_svc.list_teams(self.class_id)
        roadmaps = roadmap_svc.list_roadmaps_for_class(self.class_id)
        self._stats["Students"].set_value(str(len(students)))
        self._stats["Teams"].set_value(str(len(teams)))
        self._stats["Roadmaps"].set_value(str(len(roadmaps)))

        # Recent check-ins
        recent_checkins = checkin_svc.list_checkins_for_class(self.class_id)[:8]
        checkin_rows = [
            (
                c["id"],
                c["team"],
                c["status"],
                f"{c['week_start']} -> {c['week_end']}",
                f"{c['percent']}%",
            )
            for c in recent_checkins
        ]
        self.checkins_table.set_rows(checkin_rows)
        self._apply_checkins_filter()

        # Recent roadmaps
        roadmap_rows = [
            (
                r["id"],
                r["team"],
                r.get("principal") or "-",
                r["status"],
            )
            for r in roadmaps[:8]
        ]
        self.roadmaps_table.set_rows(roadmap_rows)
        self._apply_roadmaps_filter()

    def _apply_checkins_filter(self) -> None:
        self.checkins_table.apply_filter(
            self.checkins_filter_var.get().strip(),
            columns=(1, 2, 3, 4),
        )

    def _clear_checkins_filter(self) -> None:
        self.checkins_filter_var.set("")
        self._apply_checkins_filter()

    def _apply_roadmaps_filter(self) -> None:
        self.roadmaps_table.apply_filter(
            self.roadmaps_filter_var.get().strip(),
            columns=(1, 2, 3),
        )

    def _clear_roadmaps_filter(self) -> None:
        self.roadmaps_filter_var.set("")
        self._apply_roadmaps_filter()
