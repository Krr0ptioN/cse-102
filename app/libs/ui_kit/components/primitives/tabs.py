from __future__ import annotations

from tkinter import ttk

from ._base import ctk, use_ctk


def Tabs(master, **kwargs):  # noqa: N802
    if use_ctk(master) and ctk is not None:
        kwargs.setdefault("corner_radius", 0)
        return ctk.CTkTabview(master, **kwargs)
    return ttk.Notebook(master, **kwargs)


def add_tab(tabs, title: str, frame):
    if ctk is not None and isinstance(tabs, ctk.CTkTabview):
        tabs.add(title)
        tab = tabs.tab(title)
        frame.pack(in_=tab, fill="both", expand=True)
        return tab
    tabs.add(frame, text=title)
    return frame
