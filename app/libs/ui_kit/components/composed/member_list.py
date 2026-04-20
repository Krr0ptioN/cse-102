from __future__ import annotations

import tkinter as tk
from libs.ui_kit.theme import palette
from libs.ui_kit.design_system import Typography
from ..primitives import ScrollableFrame, Badge, Label


class MemberRow(tk.Frame):
    def __init__(self, master, name: str, email: str, role: str, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["surface"])
        super().__init__(master, bg=bg)

        content = tk.Frame(self, bg=bg, padx=12, pady=8)
        content.pack(fill="both", expand=True)

        # Avatar
        initial = name[0].upper() if name else "?"
        self.avatar = tk.Label(
            content,
            text=initial,
            bg=colors["primary"],
            fg="#ffffff",
            width=2,
            font=(Typography.primary_font_family(), 9, "bold"),
        )
        self.avatar.pack(side="left", padx=(0, 10))

        # Info
        info_frame = tk.Frame(content, bg=bg)
        info_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            info_frame,
            text=name,
            font=(Typography.primary_font_family(), 10, "bold"),
            bg=bg,
            fg=colors["text"],
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            info_frame,
            text=email,
            font=(Typography.primary_font_family(), 8),
            bg=bg,
            fg=colors["muted"],
            anchor="w",
        ).pack(fill="x")

        # Role Badge
        Badge(content, text=role, variant="outline").pack(side="right")

        # Bottom border
        tk.Frame(self, height=1, bg=colors["border"]).place(relx=0, rely=1, relwidth=1, anchor="sw")


class MemberListView(tk.Frame):
    def __init__(self, master, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)

        self.scroll_frame = ScrollableFrame(self, bg=bg)
        self.scroll_frame.pack(fill="both", expand=True)

    def set_members(self, members: list[tuple[str, str, str]]) -> None:
        """members: list of (name, email, role)"""
        self.scroll_frame.clear()
        for name, email, role in members:
            row = MemberRow(self.scroll_frame.scrollable_content, name, email, role)
            row.pack(fill="x", pady=0)
