"""Internal UI kit library (components + primitives + tokens)."""

from app.libs.ui_kit.components import __all__ as _components_all
from app.libs.ui_kit.design_system.tokens import palette
from app.libs.ui_kit.components import *  # noqa: F403

try:  # Optional; only available when customtkinter is installed.
    from app.libs.ui_kit.components.ctk_shell import CtkAppShell
except Exception:  # pragma: no cover - optional dependency
    CtkAppShell = None  # type: ignore[assignment]

__all__ = [*_components_all, "palette", "CtkAppShell"]
