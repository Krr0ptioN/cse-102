from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import button_variants
from libs.ui_kit.design_system import Typography
from libs.ui_kit import SectionHeader
from libs.ui_kit import Button, Label
from libs.ui_kit.theme import palette


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

        self.sidebar = Sidebar(
            self,
            on_back,
            nav_items or [],
            on_nav,
            context_title=title,
        )
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

        if nav_items:
            self.set_active_nav(nav_items[0][1])

    def set_active_nav(self, route: str | None) -> None:
        self.sidebar.set_active(route)


class Sidebar(tk.Frame):
    def __init__(
        self,
        master,
        on_back,
        nav_items: list[tuple[str, str]],
        on_nav=None,
        context_title: str | None = None,
    ) -> None:
        colors = palette()
        super().__init__(
            master,
            width=248,
            bg=colors["sidebar"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            bd=0,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.on_nav = on_nav
        self._buttons: dict[str, tk.Widget] = {}
        self._active_key: str | None = None

        header = tk.Frame(
            self,
            bg=colors["sidebar"],
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(14, 8))
        Label(
            header,
            text="Assignment Assistant",
            weight="bold",
            bg=colors["sidebar"],
            font=(Typography.primary_font_family(), 14, "bold"),
        ).pack(anchor="w")
        Label(
            header,
            text=context_title or "Workspace",
            variant="muted",
            bg=colors["sidebar"],
            font=(Typography.primary_font_family(), 10),
        ).pack(anchor="w", pady=(2, 0))

        Label(
            self,
            text="Navigation",
            variant="muted",
            bg=colors["sidebar"],
            font=(Typography.primary_font_family(), 9, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 6))

        self.nav = tk.Frame(self, bg=colors["sidebar"])
        self.nav.grid(row=2, column=0, sticky="nsew", padx=10)

        for label, key in nav_items:
            btn = Button(
                self.nav,
                text=label,
                variant="secondary",
                size="sm",
                anchor="w",
                command=(lambda k=key: self._handle_nav(k)),
            )
            btn.pack(fill="x", pady=4)
            self._buttons[key] = btn

        footer = tk.Frame(self, bg=colors["sidebar"])
        footer.grid(row=3, column=0, sticky="ew", padx=10, pady=12)
        Button(
            footer,
            text="Back",
            command=on_back,
            variant="outline",
            size="sm",
        ).pack(fill="x")

    def _handle_nav(self, key: str) -> None:
        if self.on_nav:
            self.on_nav(key)

    def set_active(self, key: str | None) -> None:
        self._active_key = key if key in self._buttons else None
        for route, button in self._buttons.items():
            self._apply_button_style(button, active=route == self._active_key)

    @staticmethod
    def _apply_button_style(button, *, active: bool) -> None:
        variant_key = "default" if active else "secondary"
        tokens = button_variants()[variant_key]
        button.configure(
            bg=tokens.bg,
            fg=tokens.fg,
            activebackground=tokens.hover,
            activeforeground=tokens.fg,
            highlightbackground=tokens.border,
            highlightcolor=tokens.border,
            highlightthickness=1,
        )


class Topbar(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        tk.Label(
            self,
            text=title,
            font=(Typography.primary_font_family(), 18, "bold"),
            bg=colors["panel"],
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
