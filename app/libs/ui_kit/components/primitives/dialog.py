from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.design_system.semantic_tokens import semantic_colors
from app.libs.ui_kit.components.primitives._base import ctk, use_ctk


class Dialog:
    def __init__(self, master, title: str) -> None:
        colors = semantic_colors()
        if use_ctk(master) and ctk is not None:
            self.window = ctk.CTkToplevel(master)
            self.window.configure(fg_color=colors.surface)
            body_cls = ctk.CTkFrame
            body_kwargs = {"fg_color": "transparent"}
        else:
            self.window = tk.Toplevel(master)
            self.window.configure(bg=colors.panel)
            body_cls = tk.Frame
            body_kwargs = {"bg": colors.panel}

        self.window.title(title)
        self.window.transient(master)
        self.window.grab_set()
        self.body = body_cls(self.window, **body_kwargs)
        self.body.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        self.actions = body_cls(self.window, **body_kwargs)
        self.actions.pack(fill="x", padx=16, pady=(0, 16))

    def destroy(self) -> None:
        self.window.destroy()
