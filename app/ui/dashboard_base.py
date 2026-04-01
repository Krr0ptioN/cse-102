from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.ui.components.composed import topbar_action
from app.ui.components import AppShell, TeamDrawer
from app.ui.shell_factory import resolve_shell


class DashboardBase(tk.Frame):
    """Shared scaffold for role dashboards.

    Provides the AppShell, a common content grid, a reusable drawer, and
    convenience helpers for subclasses to attach actions and layout pieces.
    """

    def __init__(
        self,
        master,
        title: str,
        on_back,
        drawer_title: str = "Details",
        nav_items: list[tuple[str, str]] | None = None,
        on_nav=None,
        shell_cls=None,
    ) -> None:
        super().__init__(master)
        self.on_back = on_back

        shell_class = shell_cls or resolve_shell()
        self.shell = shell_class(
            self, title, on_back, nav_items=nav_items, on_nav=on_nav
        )
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

    def add_topbar_button(self, text: str, command, side: str = "left") -> None:
        topbar_action(self.shell.topbar.actions, text=text, command=command, side=side)

    def add_demo_button(self) -> None:
        self.add_topbar_button("Demo", self._show_demo_notice, side="right")

    def _show_demo_notice(self) -> None:
        messagebox.showinfo(
            "Demo Dataset",
            "You are currently viewing mock/demo data initialized at startup.",
        )

    def swap_content(self, frame: tk.Frame) -> None:
        """Replace current content with provided frame."""
        for child in self.shell.content.winfo_children():
            if child is frame:
                continue
            child.destroy()
        frame.pack(fill="both", expand=True)

    # ----- Template methods -----------------------------------------------
    def build_layout(
        self,
    ) -> None:  # pragma: no cover - to be implemented by subclasses
        raise NotImplementedError
