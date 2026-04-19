from __future__ import annotations

from libs.ui_kit import Button


def topbar_action(master, *, text: str, command, side: str = "left"):
    btn = Button(master, text=text, command=command, variant="outline", size="sm")
    btn.pack(side=side, padx=6)
    return btn
