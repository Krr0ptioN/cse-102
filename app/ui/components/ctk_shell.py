from __future__ import annotations

import customtkinter as ctk

from app.design_system.typography import Typography
from app.ui.design.tokens import palette, spacing


FONT_FAMILY = Typography.primary_font_family()


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

        self.sidebar = CtkSidebar(self, on_back, nav_items or [], on_nav)
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


class CtkSidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_back,
        nav_items: list[tuple[str, str]],
        on_nav=None,
    ) -> None:
        colors = palette()
        super().__init__(
            master, width=240, fg_color=colors["surface_alt"], corner_radius=0
        )
        self.grid_propagate(False)
        self.on_nav = on_nav

        pad = spacing("md")
        ctk.CTkLabel(
            self,
            text="Lifecycle",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=colors["text"],
        ).pack(anchor="w", padx=pad, pady=(pad, 4))
        ctk.CTkLabel(
            self,
            text="Project Manager",
            font=(FONT_FAMILY, 11),
            text_color=colors["muted"],
        ).pack(anchor="w", padx=pad, pady=(0, pad))

        self.nav = ctk.CTkFrame(self, fg_color=colors["surface_alt"])
        self.nav.pack(fill="x", padx=pad)

        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.nav,
                text=label,
                fg_color=colors["surface"],
                bg_color=colors["surface_alt"],
                hover_color=colors["accent_soft"],
                text_color=colors["text"],
                anchor="w",
                corner_radius=0,
                border_width=1,
                border_color=colors["border"],
                height=36,
                command=(lambda k=key: self.on_nav(k)) if self.on_nav else None,
            )
            btn.pack(fill="x", pady=spacing("xxs"))

        ctk.CTkButton(
            self,
            text="Back",
            fg_color=colors["accent"],
            hover_color=colors["accent"],
            text_color="#ffffff",
            bg_color=colors["surface_alt"],
            corner_radius=0,
            height=40,
            command=on_back,
        ).pack(side="bottom", fill="x", padx=pad, pady=spacing("md"))


class CtkTopbar(ctk.CTkFrame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, fg_color=colors["surface"], corner_radius=0)
        pad = spacing("md")
        ctk.CTkLabel(
            self, text=title, font=(FONT_FAMILY, 18, "bold"), text_color=colors["text"]
        ).pack(side="left", padx=pad, pady=pad)
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(side="right", padx=pad)
