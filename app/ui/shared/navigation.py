from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, Optional

if TYPE_CHECKING:
    from app.ui.shared.page import Page


@dataclass
class PageMeta:
    title: str
    icon: str | None = None
    visible: bool = True


PageFactory = Callable[[object, dict], "Page"]


class Navigation:
    def __init__(
        self, registry: Dict[str, tuple[PageMeta, PageFactory]], default_route: str
    ) -> None:
        self._registry = registry
        self.default_route = default_route

    def get_factory(self, route: str) -> Optional[PageFactory]:
        entry = self._registry.get(route)
        return entry[1] if entry else None

    def get_meta(self, route: str) -> Optional[PageMeta]:
        entry = self._registry.get(route)
        return entry[0] if entry else None

    def items(self) -> list[tuple[str, PageMeta]]:
        return [(k, v[0]) for k, v in self._registry.items() if v[0].visible]
