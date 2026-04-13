from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import Button, Card, SectionHeader
from app.ui.student.stats import StudentStatsRow


class StudentOverviewPage(tk.Frame):
    def __init__(self, master, on_open_page) -> None:
        bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=bg)
        self._on_open_page = on_open_page
        self._build()

    def _build(self) -> None:
        self.stats_row = StudentStatsRow(self)
        self.stats_row.pack(fill="x", padx=12, pady=(0, 8))

class StudentSectionPage(tk.Frame):
    def __init__(self, master, *, title: str, subtitle: str | None = None) -> None:
        bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=bg)
        SectionHeader(self, title=title, subtitle=subtitle).pack(
            fill="x", padx=12, pady=(12, 8)
        )
        self.body = tk.Frame(self, bg=self["bg"])
        self.body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
