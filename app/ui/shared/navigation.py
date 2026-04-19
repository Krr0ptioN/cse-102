from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.shared.page import Page


RouteKey = str


@dataclass(frozen=True, slots=True)
class PageMeta:
    title: str
    icon: str | None = None
    visible: bool = True


PageFactory = Callable[[object, dict], "Page"]
RegistryEntry = tuple[PageMeta, PageFactory]


class Navigation:
    def __init__(
        self,
        registry: Mapping[RouteKey, RegistryEntry],
        default_route: RouteKey,
    ) -> None:
        self._registry: dict[RouteKey, RegistryEntry] = dict(registry)
        self.default_route = default_route

    def get_factory(self, route: RouteKey) -> PageFactory | None:
        entry = self._registry.get(route)
        return entry[1] if entry else None

    def get_meta(self, route: RouteKey) -> PageMeta | None:
        entry = self._registry.get(route)
        return entry[0] if entry else None

    def items(self) -> list[tuple[RouteKey, PageMeta]]:
        return [(k, v[0]) for k, v in self._registry.items() if v[0].visible]
