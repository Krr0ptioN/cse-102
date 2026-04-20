from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

from libs.logger import get_logger
from libs.ui_kit import topbar_action
from libs.ui_kit import AppShell, TeamDrawer
from .shell_factory import resolve_shell

if TYPE_CHECKING:
    from ui.shared.page import Page


class DashboardBase(tk.Frame):
    """Shared scaffold for role dashboards.

    Provides the AppShell, a common content grid, and a right-side Slide-Over
    panel (slide_over) for contextual details and comments.
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
        self.shell = shell_class(
            self, title, on_back, nav_items=[], on_nav=self._on_nav
        )
        self.shell.pack(fill="both", expand=True)
        
        # Slide-Over Panel (Contextual Sidebar)
        # We use TeamDrawer which supports render_team_header
        self.slide_over = TeamDrawer(self.shell.content, drawer_title)

        # Content area for pages
        self.page_host = tk.Frame(self.shell.content, bg=self.shell.content["bg"])
        self.page_host.grid(row=0, column=0, sticky="nsew")
        
        # Configure Grid: Column 0 is main content, Column 1 is Slide-Over
        self.shell.content.grid_rowconfigure(0, weight=1)
        self.shell.content.grid_columnconfigure(0, weight=1)
        self.shell.content.grid_columnconfigure(1, weight=0, minsize=300) # Fixed width for slide-over

        self.log.info("Dashboard initialized: %s", title)
        self.build_layout()

    def build_layout(self) -> None:
        """Subclasses should implement this to register pages and configure initial UI."""
        self.mount_slide_over()

    def register_page(self, page: Page) -> None:
        """Register a page instance and add it to the navigation."""
        if not page.route:
            self.log.error("Page %s has no route defined", page.__class__.__name__)
            return
        
        self.pages[page.route] = page
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

    def configure_content_grid(
        self, column_weights: tuple[int, ...], drawer_minsize: int = 300
    ) -> None:
        """Apply consistent grid weights on the shell content area."""
        content = self.shell.content
        for idx, weight in enumerate(column_weights):
            if idx == 1 and drawer_minsize:
                content.grid_columnconfigure(idx, weight=weight, minsize=drawer_minsize)
            else:
                content.grid_columnconfigure(idx, weight=weight)

    def mount_slide_over(self, row: int = 0, column: int = 1, rowspan: int = 1) -> None:
        """Display the slide-over panel on the right side."""
        self.slide_over.grid(
            row=row, column=column, rowspan=rowspan, sticky="nsew", padx=8, pady=8
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
