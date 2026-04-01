from __future__ import annotations

import tkinter as tk

from app.ui.components.primitives import Button
from app.ui.theme import palette


class ButtonBar(tk.Frame):
    def __init__(self, master) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        self.colors = colors

    def add(self, text: str, command, side: str = "left") -> tk.Button:
        btn = Button(
            self,
            text=text,
            command=command,
            variant="secondary",
            size="sm",
        )
        btn.pack(side=side, padx=4, pady=2)
        return btn


def bind_modal_keys(modal: tk.Toplevel, on_save) -> None:
    modal.bind("<Escape>", lambda _e: modal.destroy())
    modal.bind("<Return>", lambda _e: on_save())
