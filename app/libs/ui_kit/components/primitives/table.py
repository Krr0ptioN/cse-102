from __future__ import annotations

import tkinter.font as tkfont
from tkinter import ttk

from libs.ui_kit.design_system import semantic_colors
from libs.ui_kit import tk_style


class Table(ttk.Treeview):
    def __init__(
        self,
        master,
        columns: list[str],
        height: int = 6,
        *,
        sortable: bool = True,
        striped: bool = True,
    ) -> None:
        self._columns = tuple(columns)
        self._sortable = sortable
        self._striped = striped
        self._sort_column: str | None = None
        self._sort_reverse = False
        self._raw_rows: list[tuple] = []
        self._active_rows: list[tuple] = []
        self._filter_query = ""
        self._filter_columns: tuple[int, ...] | None = None

        tk_style(master)
        super().__init__(
            master,
            columns=columns,
            show="headings",
            height=height,
            style="Ds.Treeview",
        )

        self._configure_row_tags()
        self._update_headings()
        for col in self._columns:
            self._set_initial_column_style(col)

    def set_rows(self, rows: list[tuple]) -> None:
        self._raw_rows = list(rows)
        self._apply_filter_sort_and_render()

    def apply_filter(self, query: str, columns: tuple[int, ...] | None = None) -> None:
        self._filter_query = query.strip().lower()
        self._filter_columns = columns
        self._apply_filter_sort_and_render()

    def clear_filter(self) -> None:
        self.apply_filter("")

    def sort_by(self, column: str) -> None:
        if not self._sortable:
            return
        if column == self._sort_column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        self._apply_filter_sort_and_render()

    def _apply_filter_sort_and_render(self) -> None:
        rows = list(self._raw_rows)
        if self._filter_query:
            rows = [
                row for row in rows if self._matches_filter(row, self._filter_query)
            ]

        if self._sort_column and self._sort_column in self._columns:
            sort_idx = self._columns.index(self._sort_column)
            rows.sort(
                key=lambda row: self._sort_key(
                    row[sort_idx] if sort_idx < len(row) else ""
                ),
                reverse=self._sort_reverse,
            )

        self._active_rows = rows
        self._render_rows(rows)
        self._sync_column_widths(rows)
        self._update_headings()

    def _render_rows(self, rows: list[tuple]) -> None:
        for item in self.get_children():
            self.delete(item)

        for idx, row in enumerate(rows):
            tags: tuple[str, ...] = ()
            if self._striped:
                tags = ("row_even" if idx % 2 == 0 else "row_odd",)
            self.insert("", "end", values=row, tags=tags)

    def _matches_filter(self, row: tuple, query: str) -> bool:
        if not row:
            return False
        if self._filter_columns:
            indices = [i for i in self._filter_columns if 0 <= i < len(row)]
        else:
            indices = list(range(len(row)))

        for idx in indices:
            if query in str(row[idx]).lower():
                return True
        return False

    def _sort_key(self, value):
        if value is None:
            return (3, "")
        if isinstance(value, (int, float)):
            return (0, float(value))

        text = str(value).strip()
        if not text:
            return (3, "")

        if text.endswith("%"):
            number = text[:-1].strip().replace(",", "")
            try:
                return (0, float(number))
            except ValueError:
                pass

        normalized = text.replace(",", "")
        try:
            return (0, int(normalized))
        except ValueError:
            pass

        try:
            return (1, float(normalized))
        except ValueError:
            return (2, text.lower())

    def _update_headings(self) -> None:
        for col in self._columns:
            heading_text = col
            if col == self._sort_column:
                heading_text = f"{col} {'▼' if self._sort_reverse else '▲'}"

            heading_kwargs = {"text": heading_text}
            if self._sortable:
                heading_kwargs["command"] = lambda c=col: self.sort_by(c)
            self.heading(col, **heading_kwargs)

    def _configure_row_tags(self) -> None:
        colors = semantic_colors()
        self.tag_configure("row_even", background=colors.surface)
        self.tag_configure("row_odd", background=colors.panel)

    def _set_initial_column_style(self, col: str) -> None:
        if col.strip().lower() == "id":
            self.column(col, anchor="center", width=80, stretch=False)
            return
        self.column(col, anchor="w", width=140, stretch=True)

    def _sync_column_widths(self, rows: list[tuple]) -> None:
        try:
            font = tkfont.nametofont("TkDefaultFont")
            measure = font.measure
        except Exception:
            measure = lambda text: max(7 * len(str(text)), 70)

        sample_rows = rows[:200]
        for idx, col in enumerate(self._columns):
            if col.strip().lower() == "id":
                continue

            max_px = measure(col) + 28
            for row in sample_rows:
                if idx >= len(row):
                    continue
                max_px = max(max_px, measure(str(row[idx])) + 24)

            width = min(max(max_px, 120), 520)
            self.column(col, width=width, stretch=True)
