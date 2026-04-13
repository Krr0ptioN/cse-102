from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    Label,
    SectionHeader,
)
from app.libs.ui_kit.theme import palette


class CheckinsSection(tk.Frame):
    def __init__(self, master, on_select, on_comment, on_approve) -> None:
        colors_bg = (
            master["bg"] if isinstance(master, tk.BaseWidget) else palette()["bg"]
        )
        super().__init__(master, bg=colors_bg)
        self.on_select = on_select
        self.on_comment = on_comment
        self.on_approve = on_approve
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Check-ins",
            subtitle="Track progress updates and provide teacher feedback.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        table_card = Card(self)
        table_card.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        Label(table_card, text="Weekly Check-ins", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.checkin_filter_var = tk.StringVar(value="")
        checkin_filter_row = tk.Frame(table_card, bg=table_card["bg"])
        checkin_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(checkin_filter_row, text="Filter", bg=table_card["bg"]).pack(
            side="left"
        )
        self.checkin_filter_entry = Input(
            checkin_filter_row,
            width=30,
            textvariable=self.checkin_filter_var,
        )
        self.checkin_filter_entry.pack(side="left", padx=(8, 8))
        self.checkin_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_checkin_filter(),
        )
        Button(
            checkin_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_checkin_filter,
        ).pack(side="left")

        self.table = DataTable(
            table_card,
            ["Id", "Team", "Week", "Status", "Progress", "Submitted"],
            height=8,
        )
        self.table.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

        actions = ButtonBar(table_card)
        actions.pack(fill="x", padx=12, pady=(0, 12))
        actions.add("Add Comment", self.on_comment)
        actions.add("Approve", self.on_approve, side="right")

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

    def set_rows(self, rows: list[tuple]) -> None:
        self.table.set_rows(rows)
        self._apply_checkin_filter()

    def set_comment_rows(self, rows: list[tuple]) -> None:
        self.comment_table.set_rows(rows)
        self._apply_comment_filter()

    def selected_id(self) -> int | None:
        selection = self.table.selection()
        if not selection:
            return None
        return int(self.table.item(selection[0], "values")[0])

    def selected_row(self) -> tuple | None:
        selection = self.table.selection()
        if not selection:
            return None
        return self.table.item(selection[0], "values")

    def _apply_checkin_filter(self) -> None:
        self.table.apply_filter(
            self.checkin_filter_var.get().strip(),
            columns=(1, 2, 3, 4, 5),
        )

    def _clear_checkin_filter(self) -> None:
        self.checkin_filter_var.set("")
        self._apply_checkin_filter()

    def _apply_comment_filter(self) -> None:
        self.comment_table.apply_filter(
            self.comment_filter_var.get().strip(), columns=(0, 1)
        )

    def _clear_comment_filter(self) -> None:
        self.comment_filter_var.set("")
        self._apply_comment_filter()
