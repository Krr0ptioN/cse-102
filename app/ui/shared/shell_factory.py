from __future__ import annotations

import os

from app.libs.ui_kit.components import AppShell

try:  # Optional; only used when APP_UI=ctk
    from app.libs.ui_kit.components.ctk_shell import CtkAppShell
except Exception:  # pragma: no cover - fallback if customtkinter unavailable
    CtkAppShell = None  # type: ignore


def resolve_shell():
    flavor = os.getenv("APP_UI", "tk").lower()
    if flavor == "ctk" and CtkAppShell is not None:
        return CtkAppShell
    return AppShell
