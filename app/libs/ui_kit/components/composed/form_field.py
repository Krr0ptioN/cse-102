from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import semantic_colors
from libs.ui_kit import ctk, use_ctk
from libs.ui_kit import Label


class FormField:
    """Small field wrapper: label + control + message."""

    def __init__(self, master, *, label: str, control) -> None:
        colors = semantic_colors()
        if use_ctk(master) and ctk is not None:
            self.frame = ctk.CTkFrame(master, fg_color="transparent")
            self.message = ctk.CTkLabel(
                self.frame,
                text="",
                text_color=colors.muted,
                anchor="w",
            )
        else:
            self.frame = tk.Frame(master, bg=colors.bg)
            self.message = tk.Label(
                self.frame,
                text="",
                fg=colors.muted,
                bg=colors.bg,
                anchor="w",
            )

        self.label_widget = Label(self.frame, text=label)
        self.control = control
        self.label_widget.pack(anchor="w", pady=(0, 4))
        self.control.pack(fill="x")
        self.message.pack(anchor="w", pady=(4, 0))

    def pack(self, **kwargs) -> None:
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.frame.grid(**kwargs)

    def set_message(self, text: str, *, error: bool = False) -> None:
        colors = semantic_colors()
        self.message.configure(text=text)
        tone = colors.danger if error else colors.muted
        key = "text_color" if use_ctk(self.message) else "fg"
        self.message.configure(**{key: tone})
