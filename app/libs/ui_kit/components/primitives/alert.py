from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.design_system.semantic_tokens import semantic_colors
from app.libs.ui_kit.design_system.typography import Typography
from app.libs.ui_kit.design_system.variants import normalize_option
from app.libs.ui_kit.components.primitives._base import ctk, use_ctk


ALERT_VARIANTS = ("info", "success", "warning", "danger")


def Alert(  # noqa: N802
    master,
    *,
    title: str,
    description: str = "",
    variant: str = "info",
):
    colors = semantic_colors()
    selected = normalize_option(variant, ALERT_VARIANTS, "info")
    tone = {
        "info": (colors.primary_soft, colors.text),
        "success": ("#dcfce7", colors.text),
        "warning": ("#fef3c7", colors.text),
        "danger": ("#fee2e2", colors.text),
    }
    bg, fg = tone[selected]
    title_font = (Typography.primary_font_family(), 12, "bold")
    title_font_tk = (Typography.primary_font_family(), 11, "bold")

    if use_ctk(master) and ctk is not None:
        container = ctk.CTkFrame(
            master,
            fg_color=bg,
            border_color=colors.border,
            border_width=1,
            corner_radius=0,
        )
        container.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            container,
            text=title,
            text_color=fg,
            font=title_font,
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        if description:
            ctk.CTkLabel(
                container,
                text=description,
                text_color=fg,
                justify="left",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
        return container

    container = tk.Frame(
        master,
        bg=bg,
        highlightbackground=colors.border,
        highlightthickness=1,
        bd=0,
    )
    tk.Label(container, text=title, bg=bg, fg=fg, font=title_font_tk).pack(
        anchor="w", padx=12, pady=(10, 4)
    )
    if description:
        tk.Label(container, text=description, bg=bg, fg=fg, justify="left").pack(
            anchor="w", padx=12, pady=(0, 10)
        )
    return container
