from __future__ import annotations

import tkinter as tk
from typing import Literal

from .primitives._base import frame_bg_kwargs
from ..design_system import core_spacing

SpacingToken = Literal["xxs", "xs", "sm", "md", "lg", "xl"]
SpacingValue = int | SpacingToken
FlexDirection = Literal["row", "column"]


def _resolve_spacing(value: SpacingValue) -> int:
    if isinstance(value, int):
        return max(0, value)
    tokens = core_spacing()
    return max(0, int(getattr(tokens, value, tokens.sm)))


class Flex(tk.Frame):
    """Simple flex-like layout utility for Tk/CTk screens.

    Children are packed in order through `add(...)`.
    """

    def __init__(
        self,
        master,
        *,
        direction: FlexDirection = "row",
        gap: SpacingValue = "sm",
        panel: bool = False,
        **kwargs,
    ) -> None:
        frame_kwargs = frame_bg_kwargs(panel=panel)
        frame_kwargs.update(kwargs)
        super().__init__(master, **frame_kwargs)
        self.direction: FlexDirection = direction if direction in ("row", "column") else "row"
        self.gap = _resolve_spacing(gap)
        self._item_count = 0

    def add(
        self,
        widget,
        *,
        grow: bool = False,
        fill: str | None = None,
        expand: bool | None = None,
        padx: int | tuple[int, int] | None = None,
        pady: int | tuple[int, int] | None = None,
        **pack_kwargs,
    ):
        side = "left" if self.direction == "row" else "top"

        if fill is None:
            if grow:
                fill = "y" if self.direction == "row" else "x"
            else:
                fill = "none"

        if expand is None:
            expand = bool(grow)

        if padx is None:
            if self.direction == "row":
                padx = (0 if self._item_count == 0 else self.gap, 0)
            else:
                padx = 0
        if pady is None:
            if self.direction == "column":
                pady = (0 if self._item_count == 0 else self.gap, 0)
            else:
                pady = 0

        widget.pack(
            side=side,
            fill=fill,
            expand=expand,
            padx=padx,
            pady=pady,
            **pack_kwargs,
        )
        self._item_count += 1
        return widget

    def push(self):
        """Insert an expanding spacer."""
        spacer = tk.Frame(self, **frame_bg_kwargs(panel=False))
        if self.direction == "row":
            spacer.pack(side="left", fill="x", expand=True)
        else:
            spacer.pack(side="top", fill="y", expand=True)
        self._item_count += 1
        return spacer

    def clear(self) -> None:
        for child in list(self.winfo_children()):
            child.destroy()
        self._item_count = 0

    def set_gap(self, gap: SpacingValue) -> None:
        self.gap = _resolve_spacing(gap)


class Grid(tk.Frame):
    """Grid layout utility with spacing tokens and simple auto-placement."""

    def __init__(
        self,
        master,
        *,
        columns: int | None = None,
        rows: int | None = None,
        gap: SpacingValue = "sm",
        gap_x: SpacingValue | None = None,
        gap_y: SpacingValue | None = None,
        panel: bool = False,
        **kwargs,
    ) -> None:
        frame_kwargs = frame_bg_kwargs(panel=panel)
        frame_kwargs.update(kwargs)
        super().__init__(master, **frame_kwargs)

        self.columns = max(0, int(columns or 0))
        self.rows = max(0, int(rows or 0))
        base_gap = _resolve_spacing(gap)
        self.gap_x = _resolve_spacing(gap_x) if gap_x is not None else base_gap
        self.gap_y = _resolve_spacing(gap_y) if gap_y is not None else base_gap

        self._cursor_index = 0

        if self.columns:
            for col in range(self.columns):
                self.grid_columnconfigure(col, weight=1)
        if self.rows:
            for row in range(self.rows):
                self.grid_rowconfigure(row, weight=0)

    def _resolve_cell(self, row: int | None, column: int | None) -> tuple[int, int]:
        if row is not None and column is not None:
            return row, column

        if self.columns <= 0:
            auto_row = self._cursor_index
            self._cursor_index += 1
            return auto_row, 0

        auto_row = self._cursor_index // self.columns
        auto_col = self._cursor_index % self.columns
        self._cursor_index += 1
        return auto_row, auto_col

    def add(
        self,
        widget,
        *,
        row: int | None = None,
        column: int | None = None,
        row_span: int = 1,
        col_span: int = 1,
        sticky: str = "nsew",
        padx: int | tuple[int, int] | None = None,
        pady: int | tuple[int, int] | None = None,
        **grid_kwargs,
    ):
        row_idx, col_idx = self._resolve_cell(row, column)
        if padx is None:
            padx = (0 if col_idx == 0 else self.gap_x, 0)
        if pady is None:
            pady = (0 if row_idx == 0 else self.gap_y, 0)

        widget.grid(
            row=row_idx,
            column=col_idx,
            rowspan=max(1, row_span),
            columnspan=max(1, col_span),
            sticky=sticky,
            padx=padx,
            pady=pady,
            **grid_kwargs,
        )
        return widget

    def set_column_weights(self, *weights: int, uniform: str | None = None) -> None:
        for idx, weight in enumerate(weights):
            self.grid_columnconfigure(idx, weight=max(0, int(weight)), uniform=uniform)

    def set_row_weights(self, *weights: int, uniform: str | None = None) -> None:
        for idx, weight in enumerate(weights):
            self.grid_rowconfigure(idx, weight=max(0, int(weight)), uniform=uniform)

