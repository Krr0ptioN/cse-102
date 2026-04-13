from __future__ import annotations

import tkinter as tk


class Page(tk.Frame):
    """Base page contract.

    Subclasses should set `title` and build their UI in __init__ or on_mount.
    """

    title: str = ""

    def __init__(self, master, ctx: dict) -> None:
        super().__init__(master, bg=ctx.get("bg"))
        self.ctx = ctx
        self.on_mount()

    def on_mount(self) -> None:
        """Hook for subclasses to build UI after init."""
        ...
