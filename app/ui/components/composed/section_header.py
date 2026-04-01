from __future__ import annotations

import tkinter as tk

from app.design_system.semantic_tokens import semantic_colors
from app.design_system.typography import Typography
from app.ui.components.primitives._base import ctk, use_ctk


class SectionHeader:
    def __init__(
        self,
        master,
        *,
        title: str,
        subtitle: str | None = None,
        action=None,
    ) -> None:
        colors = semantic_colors()
        if use_ctk(master) and ctk is not None:
            self.frame = ctk.CTkFrame(master, fg_color="transparent")
            title_cls = ctk.CTkLabel
            subtitle_cls = ctk.CTkLabel
            kwargs = {"text_color": colors.text}
            subtitle_kwargs = {"text_color": colors.muted}
        else:
            self.frame = tk.Frame(master, bg=colors.bg)
            title_cls = tk.Label
            subtitle_cls = tk.Label
            kwargs = {"bg": colors.bg, "fg": colors.text}
            subtitle_kwargs = {"bg": colors.bg, "fg": colors.muted}

        left = self.frame if use_ctk(master) else tk.Frame(self.frame, bg=colors.bg)
        if not use_ctk(master):
            left.pack(side="left", fill="x", expand=True)

        title_cls(
            left,
            text=title,
            font=(Typography.primary_font_family(), 14, "bold"),
            **kwargs,
        ).pack(anchor="w")
        if subtitle:
            subtitle_cls(left, text=subtitle, **subtitle_kwargs).pack(anchor="w")
        if action is not None:
            action.pack(in_=self.frame, side="right")

    def pack(self, **kwargs) -> None:
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.frame.grid(**kwargs)
