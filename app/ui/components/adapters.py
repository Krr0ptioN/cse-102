from __future__ import annotations

import os
import tkinter as tk

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional
    ctk = None


def is_ctk() -> bool:
    return os.getenv("APP_UI", "tk").lower() == "ctk" and ctk is not None


def frame(master, **kwargs):
    if is_ctk():
        fg = kwargs.pop("bg", None)
        if fg:
            kwargs.setdefault("fg_color", fg)
        return ctk.CTkFrame(master, **kwargs)
    return tk.Frame(master, **kwargs)


def label(master, **kwargs):
    if is_ctk():
        fg = kwargs.pop("fg", None)
        if fg:
            kwargs.setdefault("text_color", fg)
        bg = kwargs.pop("bg", None)
        if bg:
            kwargs.setdefault("fg_color", bg)
        return ctk.CTkLabel(master, **kwargs)
    return tk.Label(master, **kwargs)


def button(master, **kwargs):
    if is_ctk():
        fg = kwargs.pop("bg", None)
        if fg:
            kwargs.setdefault("fg_color", fg)
        hover = kwargs.pop("activebackground", None)
        if hover:
            kwargs.setdefault("hover_color", hover)
        fg_text = kwargs.pop("fg_text", None)
        if fg_text:
            kwargs.setdefault("text_color", fg_text)
        return ctk.CTkButton(master, **kwargs)
    return tk.Button(master, **kwargs)
