from __future__ import annotations

from libs.ui_kit import ButtonBar, DataTable, Section


class StudentCommentsSection(Section):
    def __init__(self, master, on_add_comment) -> None:
        super().__init__(master, "Roadmap Comments")
        self.on_add_comment = on_add_comment
        self._build()

    def _build(self) -> None:
        action = ButtonBar(self.body)
        action.pack(fill="x", pady=4)
        action.add("Add Comment", self.on_add_comment)

        self.comment_table = DataTable(self.body, ["Author", "Comment", "Time"], height=5)
        self.comment_table.pack(fill="both", expand=True, pady=6)

    def set_comment_rows(self, rows: list[tuple]) -> None:
        self.comment_table.set_rows(rows)
