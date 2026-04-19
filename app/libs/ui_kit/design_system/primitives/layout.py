from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import palette


class Container(tk.Frame):
    def __init__(self, master, padding: int = 12, **kwargs) -> None:
        colors = palette()
        super().__init__(master, bg=kwargs.get("bg", colors.bg))
        self._pad = padding
