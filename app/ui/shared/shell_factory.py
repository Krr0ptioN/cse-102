from __future__ import annotations

import os

from libs.ui_kit import AppShell, CtkAppShell


def resolve_shell():
    flavor = os.getenv("APP_UI", "tk").lower()
    if flavor == "ctk" and CtkAppShell is not None:
        return CtkAppShell
    return AppShell
