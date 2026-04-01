from __future__ import annotations

import customtkinter as ctk

from app.ui.design.tokens import palette, spacing


class CtkButton(ctk.CTkButton):
    def __init__(self, master, *, variant: str = "primary", **kwargs) -> None:
        colors = palette()
        fg = colors["accent"] if variant == "primary" else colors["surface"]
        hover = colors["accent"] if variant == "primary" else colors["accent_soft"]
        text = "#ffffff" if variant == "primary" else colors["text"]
        super().__init__(
            master,
            fg_color=fg,
            hover_color=hover,
            text_color=text,
            corner_radius=0,
            **kwargs,
        )


class CtkInput(ctk.CTkEntry):
    def __init__(self, master, **kwargs) -> None:
        colors = palette()
        super().__init__(
            master,
            corner_radius=0,
            fg_color=colors["surface"],
            border_color=colors["border"],
            text_color=colors["text"],
            **kwargs,
        )


class CtkCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        colors = palette()
        super().__init__(
            master,
            fg_color=colors["surface"],
            corner_radius=0,
            **kwargs,
        )
        pad = spacing("md")
        self.columnconfigure(0, weight=1)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(
            row=0, column=0, sticky="ew", padx=pad, pady=(pad, spacing("xs"))
        )
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=pad, pady=(0, pad))
        self.rowconfigure(1, weight=1)


class CtkModal(ctk.CTkToplevel):
    def __init__(self, master, title: str) -> None:
        super().__init__(master)
        colors = palette()
        self.title(title)
        self.configure(fg_color=colors["surface"])
        pad = spacing("md")
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=pad, pady=(pad, spacing("sm")))
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(fill="x", padx=pad, pady=(0, pad))
        self.grab_set()


class CtkProgress(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs) -> None:
        colors = palette()
        super().__init__(
            master,
            fg_color=colors["surface_alt"],
            progress_color=colors["accent"],
            **kwargs,
        )
