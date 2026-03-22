from __future__ import annotations

import tkinter as tk

from app.ui.components import AppShell, TeamDrawer


class DashboardBase(tk.Frame):
    """Shared scaffold for role dashboards.

    Provides the AppShell, a common content grid, a reusable drawer, and
    convenience helpers for subclasses to attach actions and layout pieces.
    """

    def __init__(
        self, master, title: str, on_back, drawer_title: str = "Details"
    ) -> None:
        super().__init__(master)
        self.on_back = on_back

        self.shell = AppShell(self, title, on_back)
        self.shell.pack(fill="both", expand=True)

        # Drawer is available for subclasses to populate.
        self.drawer = TeamDrawer(self.shell.content, drawer_title)

        # Let subclasses build their specific UI.
        self.build_layout()

    # ----- Layout helpers -------------------------------------------------
    def configure_content_grid(
        self, column_weights: tuple[int, ...], drawer_minsize: int = 260
    ) -> None:
        """Apply consistent grid weights on the shell content area."""

        content = self.shell.content
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)

        last_index = len(column_weights) - 1
        for idx, weight in enumerate(column_weights):
            if idx == last_index and drawer_minsize:
                content.grid_columnconfigure(idx, weight=weight, minsize=drawer_minsize)
            else:
                content.grid_columnconfigure(idx, weight=weight)

    def mount_drawer(
        self, row: int, column: int, rowspan: int = 1, padx: int = 8, pady: int = 8
    ) -> None:
        self.drawer.grid(
            row=row, column=column, rowspan=rowspan, sticky="nsew", padx=padx, pady=pady
        )

    def add_topbar_button(self, text: str, command) -> None:
        tk.Button(self.shell.topbar.actions, text=text, command=command).pack(
            side="left", padx=6
        )

    # ----- Template methods -----------------------------------------------
    def build_layout(
        self,
    ) -> None:  # pragma: no cover - to be implemented by subclasses
        raise NotImplementedError
