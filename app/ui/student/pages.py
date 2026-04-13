from __future__ import annotations

import tkinter as tk

from app.ui.components import Button, Card, SectionHeader
from app.ui.student.stats import StudentStatsRow


class StudentOverviewPage(tk.Frame):
    def __init__(self, master, on_open_page) -> None:
        bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=bg)
        self._on_open_page = on_open_page
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Overview",
            subtitle="Quick snapshot and shortcuts.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        self.stats_row = StudentStatsRow(self)
        self.stats_row.pack(fill="x", padx=12, pady=(0, 8))

        quick_actions = Card(self)
        quick_actions.pack(fill="x", padx=12, pady=(0, 12))
        SectionHeader(
            quick_actions,
            title="Go to",
            subtitle="Use dedicated pages for focused work.",
        ).pack(fill="x", padx=10, pady=(10, 4))

        action_row = tk.Frame(quick_actions, bg=quick_actions["bg"])
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        Button(
            action_row,
            text="Roadmap",
            variant="secondary",
            size="sm",
            command=lambda: self._on_open_page("roadmap"),
        ).pack(side="left", padx=4)
        Button(
            action_row,
            text="Tasks",
            variant="secondary",
            size="sm",
            command=lambda: self._on_open_page("tasks"),
        ).pack(side="left", padx=4)
        Button(
            action_row,
            text="Check-ins",
            variant="secondary",
            size="sm",
            command=lambda: self._on_open_page("checkins"),
        ).pack(side="left", padx=4)
        Button(
            action_row,
            text="Comments",
            variant="secondary",
            size="sm",
            command=lambda: self._on_open_page("comments"),
        ).pack(side="left", padx=4)


class StudentSectionPage(tk.Frame):
    def __init__(self, master, *, title: str, subtitle: str | None = None) -> None:
        bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=bg)
        SectionHeader(self, title=title, subtitle=subtitle).pack(
            fill="x", padx=12, pady=(12, 8)
        )
        self.body = tk.Frame(self, bg=self["bg"])
        self.body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
