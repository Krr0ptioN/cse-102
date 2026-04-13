from __future__ import annotations

from app.libs.ui_kit.components.primitives.table import Table


class DataTable(Table):
    def __init__(self, master, columns: list[str], height: int = 6) -> None:
        super().__init__(master, columns=columns, height=height)

    def set_rows(self, rows: list[tuple]) -> None:
        super().set_rows(rows)
