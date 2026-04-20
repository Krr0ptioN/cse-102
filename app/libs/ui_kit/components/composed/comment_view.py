from __future__ import annotations

import tkinter as tk
from datetime import datetime
from ...theme import palette
from ...design_system import Typography
from ..primitives import ScrollableFrame, Button, TextArea, Label
from ..positioning import Flex
from .utils import format_timestamp


class CommentBubble(tk.Frame):
    def __init__(self, master, author: str, text: str, timestamp: str, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["panel"])
        super().__init__(master, bg=bg, pady=8)

        header = tk.Frame(self, bg=bg)
        header.pack(fill="x")

        # Avatar-like initial
        initial = author[0].upper() if author else "?"
        avatar = tk.Label(
            header,
            text=initial,
            bg=colors["primary"],
            fg="#ffffff",
            width=2,
            font=(Typography.primary_font_family(), 9, "bold"),
        )
        avatar.pack(side="left", padx=(0, 8))

        tk.Label(
            header,
            text=author,
            font=(Typography.primary_font_family(), 10, "bold"),
            bg=bg,
            fg=colors["text"],
        ).pack(side="left")

        tk.Label(
            header,
            text=format_timestamp(timestamp),
            font=(Typography.primary_font_family(), 8),
            bg=bg,
            fg=colors["muted"],
        ).pack(side="right")


        body = tk.Label(
            self,
            text=text,
            font=(Typography.primary_font_family(), 10),
            bg=bg,
            fg=colors["text"],
            justify="left",
            wraplength=220,
            anchor="w",
        )
        body.pack(fill="x", pady=(4, 0), padx=(32, 0))


class CommentThread(tk.Frame):
    def __init__(self, master, on_send=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["panel"])
        super().__init__(master, bg=bg)
        self.on_send = on_send

        self.list_frame = ScrollableFrame(self, bg=bg)
        self.list_frame.pack(fill="both", expand=True)

        self.input_area = tk.Frame(self, bg=bg, highlightbackground=colors["border"], highlightthickness=1, bd=0)
        self.input_area.pack(fill="x", pady=(8, 0))

        self.text_input = TextArea(self.input_area, height=3)
        self.text_input.pack(fill="x", padx=4, pady=4)

        btn_row = tk.Frame(self.input_area, bg=bg)
        btn_row.pack(fill="x", padx=4, pady=(0, 4))
        
        self.send_btn = Button(
            btn_row, 
            text="Send", 
            size="sm", 
            command=self._handle_send
        )
        self.send_btn.pack(side="right")

    def _handle_send(self) -> None:
        text = self.text_input.get().strip()
        if text and self.on_send:
            self.on_send(text)
            self.text_input.clear()

    def set_comments(self, comments: list[tuple[str, str, str]]) -> None:
        """comments: list of (author, text, timestamp)"""
        self.list_frame.clear()
        for author, text, timestamp in comments:
            bubble = CommentBubble(self.list_frame.scrollable_content, author, text, timestamp)
            bubble.pack(fill="x", padx=8)
