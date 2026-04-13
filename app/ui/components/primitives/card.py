from __future__ import annotations

import tkinter as tk

from app.design_system.component_tokens import card_size_tokens, card_tokens
from app.ui.components.primitives._base import ctk, use_ctk

CARD_SIZES = tuple(card_size_tokens().keys())


def _screen_axis_size(master, axis: str) -> int:
    getter = "winfo_screenwidth" if axis == "width" else "winfo_screenheight"
    targets = []
    if master is not None:
        targets.append(master)
        toplevel_getter = getattr(master, "winfo_toplevel", None)
        if callable(toplevel_getter):
            try:
                targets.insert(0, toplevel_getter())
            except Exception:
                pass

    for target in targets:
        fn = getattr(target, getter, None)
        if callable(fn):
            try:
                value = int(fn())
            except Exception:
                continue
            if value > 0:
                return value
    return 1920 if axis == "width" else 1080


def _resolve_dimension(value, *, axis: str, master) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return max(1, int(value))

    raw = str(value).strip().lower()
    if not raw:
        return None

    size_tokens = card_size_tokens()
    if raw in size_tokens:
        return int(size_tokens[raw][axis])

    if raw.endswith("px"):
        raw = raw[:-2].strip()
        try:
            return max(1, int(float(raw)))
        except ValueError:
            return None

    if raw.endswith("vw") and axis == "width":
        try:
            ratio = float(raw[:-2].strip()) / 100.0
        except ValueError:
            return None
        return max(1, int(_screen_axis_size(master, "width") * ratio))

    if raw.endswith("vh") and axis == "height":
        try:
            ratio = float(raw[:-2].strip()) / 100.0
        except ValueError:
            return None
        return max(1, int(_screen_axis_size(master, "height") * ratio))

    if raw.endswith("%"):
        try:
            ratio = float(raw[:-1].strip()) / 100.0
        except ValueError:
            return None
        return max(1, int(_screen_axis_size(master, axis) * ratio))

    try:
        return max(1, int(float(raw)))
    except ValueError:
        return None


def Card(  # noqa: N802
    master,
    *,
    variant: str = "default",
    size: str | None = None,
    width: int | float | str | None = None,
    height: int | float | str | None = None,
    **kwargs,
):
    del variant  # reserved for future variants
    tokens = card_tokens()
    selected_size = str(size).lower().strip() if size is not None else None
    if selected_size and selected_size not in CARD_SIZES:
        selected_size = None

    default_width = None
    default_height = None
    if selected_size:
        size_tokens = card_size_tokens()[selected_size]
        default_width = int(size_tokens["width"])
        default_height = int(size_tokens["height"])

    resolved_width = _resolve_dimension(
        width if width is not None else default_width, axis="width", master=master
    )
    resolved_height = _resolve_dimension(
        height if height is not None else default_height, axis="height", master=master
    )

    if resolved_width is not None:
        kwargs["width"] = resolved_width
    if resolved_height is not None:
        kwargs["height"] = resolved_height

    if use_ctk(master) and ctk is not None:
        frame = ctk.CTkFrame(
            master,
            fg_color=tokens["bg"],
            border_color=tokens["border"],
            border_width=1,
            corner_radius=tokens["radius"],
            **kwargs,
        )
    else:
        frame = tk.Frame(
            master,
            bg=tokens["bg"],
            highlightbackground=tokens["border"],
            highlightthickness=1,
            bd=0,
            **kwargs,
        )

    if resolved_width is not None or resolved_height is not None:
        # Keep requested dimensions instead of shrinking/growing to child content.
        try:
            frame.pack_propagate(False)
        except Exception:
            pass
        try:
            frame.grid_propagate(False)
        except Exception:
            pass

    return frame
