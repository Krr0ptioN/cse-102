from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

from libs.logger import get_logger
from libs.ui_kit import topbar_action
from libs.ui_kit import AppShell, TeamDrawer
from ui.shared import resolve_shell

if TYPE_CHECKING:
    from ui.shared.page import Page


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
        shell_cls=None,
    ) -> None:
        super().__init__(master)
        self.log = get_logger(f"app.ui.{self.__class__.__name__}")
        self.on_back = on_back
        self._current_page_key: str | None = None
        self.pages: dict[str, Page] = {}

        shell_class = shell_cls or resolve_shell()
        # Initialize shell without nav_items; they will be added via register_page
        self.shell = shell_class(
            self, title, on_back, nav_items=[], on_nav=self._on_nav
        )
        self.shell.pack(fill="both", expand=True)
        self.log.info("Dashboard initialized: %s", title)

        # Drawer is available for subclasses to populate.
        self.drawer = TeamDrawer(self.shell.content, drawer_title)

        # Let subclasses build their specific UI and register pages.
        self.page_host = tk.Frame(self.shell.content, bg=self.shell.content["bg"])
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.shell.content.grid_rowconfigure(1, weight=1)
        self.shell.content.grid_columnconfigure(0, weight=1)

        self.build_layout()

    def register_page(self, page: Page) -> None:
        """Register a page instance and add it to the navigation."""
        if not page.route:
            self.log.error("Page %s has no route defined", page.__class__.__name__)
            return
        
        self.pages[page.route] = page
        # Grid all pages to the same spot in page_host; we'll use lift/tkraise to switch
        page.grid(in_=self.page_host, row=0, column=0, sticky="nsew")
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

        self.shell.add_nav_item(page.title, page.route)
        self.log.debug("Registered page: %s (%s)", page.title, page.route)

    def _on_nav(self, key: str) -> None:
        self._navigate(key)

    def _navigate(self, route: str) -> None:
        if route == self._current_page_key:
            return
        
        page = self.pages.get(route)
        if not page:
            self.log.error("Navigation failed: Route '%s' not registered", route)
            return

        page.tkraise()
        self._current_page_key = route
        self.set_active_nav(route)
        page.on_show()
        self.log.info("View -> %s", route)

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

    def set_active_nav(self, route: str | None) -> None:
        set_active = getattr(self.shell, "set_active_nav", None)
        if callable(set_active):
            set_active(route)

    def add_demo_button(self) -> None:
        self.add_topbar_button("Demo", self._show_demo_notice, side="right")

    def _show_demo_notice(self) -> None:
        messagebox.showinfo(
            "Demo Dataset",
            "You are currently viewing mock/demo data initialized at startup.",
        )

    # ----- Template methods -----------------------------------------------
    def build_layout(
        self,
    ) -> None:  # pragma: no cover - to be implemented by subclasses
        raise NotImplementedError
