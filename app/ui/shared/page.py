from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.shared import DashboardBase


class Page(tk.Frame):
    """Base page contract.

    Subclasses should set `route` and `title` class attributes.
    They register themselves with the dashboard in __init__.
    """

    route: str = ""
    title: str = ""

    def __init__(self, dashboard: DashboardBase) -> None:
        super().__init__(dashboard.page_host, bg=dashboard.page_host["bg"])
        self.dashboard = dashboard
        self.dashboard.register_page(self)
        self.on_mount()

    def on_mount(self) -> None:
        """Hook for subclasses to build static UI after init."""
        ...

    def on_show(self) -> None:
        """Hook for subclasses to refresh data when navigated to."""
        ...
