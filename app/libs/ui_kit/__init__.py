"""Internal UI kit library (components + primitives + tokens)."""

from .components import __all__ as _components_all
from .design_system.tokens import palette
from .components import *  # noqa: F403
from .components.composed import __all__ as _composed_all

try:  # Optional; only available when customtkinter is installed.
    from .components.ctk_shell import CtkAppShell
except Exception:  # pragma: no cover - optional dependency
    CtkAppShell = None  # type: ignore[assignment]

__all__ = [
    *_components_all, 
    *_composed_all,
    "palette",
    "CtkAppShell",
]
