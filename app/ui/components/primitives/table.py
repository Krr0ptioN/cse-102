from __future__ import annotations

from tkinter import ttk

from app.ui.components.primitives._base import tk_style


class Table(ttk.Treeview):
    def __init__(self, master, columns: list[str], height: int = 6) -> None:
        tk_style(master)
        super().__init__(
            master,
            columns=columns,
            show="headings",
            height=height,
            style="Ds.Treeview",
        )
        for col in columns:
            self.heading(col, text=col)
            self.column(col, anchor="w", width=120, stretch=True)

    def set_rows(self, rows: list[tuple]) -> None:
        for item in self.get_children():
            self.delete(item)
        for row in rows:
            self.insert("", "end", values=row)
