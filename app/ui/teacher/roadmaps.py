from __future__ import annotations

import tkinter as tk

from app.ui.components import ButtonBar, DataTable, Section


class RoadmapReviewSection(Section):
    def __init__(self, master, on_add_comment, on_approve, on_select) -> None:
        super().__init__(master, "Roadmap Review")
        self.on_add_comment = on_add_comment
        self.on_approve = on_approve
        self.on_select = on_select
        self._build()

    def _build(self) -> None:
        self.roadmap_table = DataTable(
            self.body, ["Id", "Team", "Principal", "Status"], height=6
        )
        self.roadmap_table.pack(fill="both", expand=True, pady=6)
        self.roadmap_table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

        actions = ButtonBar(self.body)
        actions.pack(fill="x", pady=4)
        actions.add("Add Comment", self.on_add_comment)
        actions.add("Approve Selected", self.on_approve, side="right")

        self.comment_table = DataTable(self.body, ["Author", "Comment", "Time"], height=4)
        self.comment_table.pack(fill="both", expand=True, pady=6)

    def set_roadmap_rows(self, rows: list[tuple]) -> None:
        self.roadmap_table.set_rows(rows)

    def set_comment_rows(self, rows: list[tuple]) -> None:
        self.comment_table.set_rows(rows)

    def selected_roadmap_id(self) -> int | None:
        selection = self.roadmap_table.selection()
        if not selection:
            return None
        return int(self.roadmap_table.item(selection[0], "values")[0])

    def selected_roadmap_row(self) -> tuple | None:
        selection = self.roadmap_table.selection()
        if not selection:
            return None
        return self.roadmap_table.item(selection[0], "values")
