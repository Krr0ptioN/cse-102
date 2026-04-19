from __future__ import annotations

import tkinter as tk

from libs.ui_kit import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    Label,
    SectionHeader,
)
from libs.ui_kit.theme import palette


class RoadmapReviewSection(tk.Frame):
    def __init__(self, master, on_add_comment, on_approve, on_select) -> None:
        colors_bg = (
            master["bg"] if isinstance(master, tk.BaseWidget) else palette()["bg"]
        )
        super().__init__(master, bg=colors_bg)
        self.on_add_comment = on_add_comment
        self.on_approve = on_approve
        self.on_select = on_select
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Roadmap Review",
            subtitle="Review submissions, add comments, and approve ready plans.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        roadmap_card = Card(self)
        roadmap_card.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        Label(roadmap_card, text="Roadmaps", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.roadmap_filter_var = tk.StringVar(value="")
        roadmap_filter_row = tk.Frame(roadmap_card, bg=roadmap_card["bg"])
        roadmap_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(roadmap_filter_row, text="Filter", bg=roadmap_card["bg"]).pack(
            side="left"
        )
        self.roadmap_filter_entry = Input(
            roadmap_filter_row,
            width=30,
            textvariable=self.roadmap_filter_var,
        )
        self.roadmap_filter_entry.pack(side="left", padx=(8, 8))
        self.roadmap_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_roadmap_filter(),
        )
        Button(
            roadmap_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_roadmap_filter,
        ).pack(side="left")

        self.roadmap_table = DataTable(
            roadmap_card, ["Id", "Team", "Principal", "Status"], height=7
        )
        self.roadmap_table.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.roadmap_table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

        actions = ButtonBar(roadmap_card)
        actions.pack(fill="x", padx=12, pady=(0, 12))
        actions.add("Add Comment", self.on_add_comment)
        actions.add("Approve Selected", self.on_approve, side="right")

        comments_card = Card(self)
        comments_card.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        Label(comments_card, text="Comments", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.comment_filter_var = tk.StringVar(value="")
        comment_filter_row = tk.Frame(comments_card, bg=comments_card["bg"])
        comment_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(comment_filter_row, text="Filter", bg=comments_card["bg"]).pack(
            side="left"
        )
        self.comment_filter_entry = Input(
            comment_filter_row,
            width=30,
            textvariable=self.comment_filter_var,
        )
        self.comment_filter_entry.pack(side="left", padx=(8, 8))
        self.comment_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_comment_filter(),
        )
        Button(
            comment_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_comment_filter,
        ).pack(side="left")

        self.comment_table = DataTable(
            comments_card, ["Author", "Comment", "Time"], height=4
        )
        self.comment_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def set_roadmap_rows(self, rows: list[tuple]) -> None:
        self.roadmap_table.set_rows(rows)
        self._apply_roadmap_filter()

    def set_comment_rows(self, rows: list[tuple]) -> None:
        self.comment_table.set_rows(rows)
        self._apply_comment_filter()

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

    def _apply_roadmap_filter(self) -> None:
        self.roadmap_table.apply_filter(
            self.roadmap_filter_var.get().strip(),
            columns=(1, 2, 3),
        )

    def _clear_roadmap_filter(self) -> None:
        self.roadmap_filter_var.set("")
        self._apply_roadmap_filter()

    def _apply_comment_filter(self) -> None:
        self.comment_table.apply_filter(
            self.comment_filter_var.get().strip(), columns=(0, 1)
        )

    def _clear_comment_filter(self) -> None:
        self.comment_filter_var.set("")
        self._apply_comment_filter()
