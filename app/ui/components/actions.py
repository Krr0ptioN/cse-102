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


def add_modal_actions(
    modal: tk.Toplevel,
    on_confirm,
    *,
    confirm_text: str,
    cancel_text: str = "Cancel",
    bind_keys: bool = True,
    confirm_size: str = "sm",
    cancel_variant: str = "outline",
) -> None:
    if bind_keys:
        bind_modal_keys(modal, on_confirm)

    Button(
        modal.actions,
        text=cancel_text,
        command=modal.destroy,
        variant=cancel_variant,
    ).pack(side="right", padx=4)
    Button(
        modal.actions,
        text=confirm_text,
        command=on_confirm,
        size=confirm_size,
    ).pack(side="right", padx=4)
