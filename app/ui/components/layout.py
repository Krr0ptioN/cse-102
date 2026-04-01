from __future__ import annotations

import tkinter as tk

from app.design_system.typography import Typography
from app.ui.components.composed import SectionHeader
from app.ui.components.primitives import Button
from app.ui.theme import palette


FONT_FAMILY = Typography.primary_font_family()


class AppShell(tk.Frame):
    def __init__(
        self,
        master,
        title: str,
        on_back,
        nav_items: list[tuple[str, str]] | None = None,
        on_nav=None,
    ) -> None:
        colors = palette()
        super().__init__(master, bg=colors["bg"])
        self.on_back = on_back
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, on_back, nav_items or [], on_nav)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.main = tk.Frame(self, bg=colors["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.main, title)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content = tk.Frame(self.main, bg=colors["bg"])
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)


class Sidebar(tk.Frame):
    def __init__(
        self,
        master,
        on_back,
        nav_items: list[tuple[str, str]],
        on_nav=None,
    ) -> None:
        colors = palette()
        super().__init__(master, width=220, bg=colors["sidebar"])
        self.pack_propagate(False)
        self.on_nav = on_nav

        tk.Label(
            self,
            text="Lifecycle",
            font=(FONT_FAMILY, 16, "bold"),
            bg=colors["sidebar"],
            fg=colors["text"],
        ).pack(anchor="w", padx=16, pady=(16, 6))
        tk.Label(
            self,
            text="Project Manager",
            font=(FONT_FAMILY, 9),
            bg=colors["sidebar"],
            fg=colors["muted"],
        ).pack(anchor="w", padx=16, pady=(0, 16))

        self.nav = tk.Frame(self, bg=colors["sidebar"])
        self.nav.pack(fill="x", padx=10)

        for label, key in nav_items:
            btn = Button(
                self.nav,
                text=label,
                variant="secondary",
                size="sm",
                anchor="w",
                command=(lambda k=key: self.on_nav(k)) if self.on_nav else None,
            )
            btn.pack(fill="x", pady=4)

        Button(self, text="Back", command=on_back, variant="outline", size="sm").pack(
            side="bottom", fill="x", padx=10, pady=12
        )


class Topbar(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        tk.Label(
            self, text=title, font=(FONT_FAMILY, 18, "bold"), bg=colors["panel"]
        ).pack(side="left", padx=12, pady=12)
        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(side="right", padx=12)


class Section(tk.Frame):
    def __init__(self, master, title: str, subtitle: str | None = None) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            bd=0,
            padx=8,
            pady=8,
        )
        header = SectionHeader(self, title=title, subtitle=subtitle)
        header.pack(fill="x", padx=10, pady=(6, 2))
        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
