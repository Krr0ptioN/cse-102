from __future__ import annotations

from app.ui.components import ButtonBar, DataTable, Section


class CheckinsSection(Section):
    def __init__(self, master, on_select, on_comment, on_approve) -> None:
        super().__init__(master, "Check-ins")
        self.on_select = on_select
        self.on_comment = on_comment
        self.on_approve = on_approve
        self._build()

    def _build(self) -> None:
        self.table = DataTable(
            self.body,
            ["Id", "Team", "Week", "Status", "Progress", "Submitted"],
            height=8,
        )
        self.table.pack(fill="both", expand=True, pady=6)
        self.table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

        actions = ButtonBar(self.body)
        actions.pack(fill="x", pady=4)
        actions.add("Add Comment", self.on_comment)
        actions.add("Approve", self.on_approve, side="right")

        self.comment_table = DataTable(self.body, ["Author", "Comment", "Time"], height=4)
        self.comment_table.pack(fill="both", expand=True, pady=6)

    def set_rows(self, rows: list[tuple]) -> None:
        self.table.set_rows(rows)

    def set_comment_rows(self, rows: list[tuple]) -> None:
        self.comment_table.set_rows(rows)

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
