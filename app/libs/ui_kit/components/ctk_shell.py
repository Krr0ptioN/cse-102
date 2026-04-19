from __future__ import annotations

import customtkinter as ctk

from libs.ui_kit.design_system import Typography
from libs.ui_kit.design.tokens import palette, spacing


class CtkAppShell(ctk.CTkFrame):
    """CustomTkinter shell with sidebar, topbar, and content area.

    API mirrors the existing Tk AppShell to allow incremental migration.
    """

    def __init__(
        self,
        master,
        title: str,
        on_back,
        nav_items: list[tuple[str, str]] | None = None,
        on_nav=None,
    ) -> None:
        colors = palette()
        super().__init__(master, fg_color=colors["bg"])
        self.on_back = on_back
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = CtkSidebar(
            self,
            on_back,
            nav_items or [],
            on_nav,
            context_title=title,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.main = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = CtkTopbar(self.main, title)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content = ctk.CTkFrame(self.main, fg_color=colors["bg"], corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        if nav_items:
            self.set_active_nav(nav_items[0][1])

    def set_active_nav(self, route: str | None) -> None:
        self.sidebar.set_active(route)


class CtkSidebar(ctk.CTkFrame):
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
            width=260,
            fg_color=colors["surface_alt"],
            corner_radius=0,
            border_width=1,
            border_color=colors["border"],
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._colors = colors
        self.on_nav = on_nav
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._active_key: str | None = None

        pad = spacing("md")
        header = ctk.CTkFrame(
            self,
            fg_color=colors["surface_alt"],
            corner_radius=0,
        )
        header.grid(row=0, column=0, sticky="ew", padx=pad, pady=(pad, spacing("sm")))
        ctk.CTkLabel(
            header,
            text="Assignment Assistant",
            font=(Typography.primary_font_family(), 16, "bold"),
            text_color=colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=context_title or "Workspace",
            font=(Typography.primary_font_family(), 11),
            text_color=colors["muted"],
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            self,
            text="Navigation",
            font=(Typography.primary_font_family(), 10, "bold"),
            text_color=colors["muted"],
        ).grid(row=1, column=0, sticky="w", padx=pad, pady=(0, spacing("xs")))

        self.nav = ctk.CTkFrame(self, fg_color=colors["surface_alt"])
        self.nav.grid(row=2, column=0, sticky="nsew", padx=pad)

        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.nav,
                text=label,
                fg_color=colors["surface"],
                bg_color=colors["surface_alt"],
                hover_color=colors["accent_soft"],
                text_color=colors["text"],
                anchor="w",
                corner_radius=8,
                border_width=1,
                border_color=colors["border"],
                height=36,
                command=(lambda k=key: self._handle_nav(k)),
            )
            btn.pack(fill="x", pady=spacing("xxs"))
            self._buttons[key] = btn

        ctk.CTkButton(
            self,
            text="Back",
            fg_color=colors["surface"],
            hover_color=colors["surface_alt"],
            text_color=colors["text"],
            bg_color=colors["surface_alt"],
            corner_radius=8,
            border_width=1,
            border_color=colors["border"],
            height=40,
            command=on_back,
        ).grid(row=3, column=0, sticky="ew", padx=pad, pady=spacing("md"))

    def _handle_nav(self, key: str) -> None:
        if self.on_nav:
            self.on_nav(key)

    def set_active(self, key: str | None) -> None:
        self._active_key = key if key in self._buttons else None
        for route, button in self._buttons.items():
            self._apply_button_style(button, active=route == self._active_key)

    def _apply_button_style(self, button: ctk.CTkButton, *, active: bool) -> None:
        if active:
            button.configure(
                fg_color=self._colors["accent_soft"],
                text_color=self._colors["accent"],
                hover_color=self._colors["accent_soft"],
                border_color=self._colors["accent"],
            )
            return
        button.configure(
            fg_color=self._colors["surface"],
            text_color=self._colors["text"],
            hover_color=self._colors["accent_soft"],
            border_color=self._colors["border"],
        )


class CtkTopbar(ctk.CTkFrame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, fg_color=colors["surface"], corner_radius=0)
        pad = spacing("md")
        ctk.CTkLabel(
            self,
            text=title,
            font=(Typography.primary_font_family(), 18, "bold"),
            text_color=colors["text"],
        ).pack(side="left", padx=pad, pady=pad)
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(side="right", padx=pad)
