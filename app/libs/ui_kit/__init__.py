"""Internal UI kit library (components + primitives + tokens)."""

from .theme import palette
from .components import __all__ as _components_all
from .components import *  # noqa: F403

try:  # Optional; only available when customtkinter is installed.
    from .components.ctk_shell import CtkAppShell
except Exception:  # pragma: no cover - optional dependency
    CtkAppShell = None  # type: ignore[assignment]

__all__ = [
    *_components_all,
    "palette",
    "CtkAppShell",
]
