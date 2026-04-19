from __future__ import annotations

from libs.ui_kit import Button, Card, Label


class EmptyState:
    def __init__(
        self,
        master,
        *,
        title: str,
        description: str,
        action_text: str | None = None,
        action_command=None,
    ) -> None:
        self.frame = Card(master)
        Label(self.frame, text=title, weight="bold").pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        Label(self.frame, text=description, variant="muted").pack(
            anchor="w", padx=12, pady=(0, 12)
        )
        if action_text and action_command:
            Button(
                self.frame,
                text=action_text,
                command=action_command,
                variant="secondary",
                size="sm",
            ).pack(anchor="w", padx=12, pady=(0, 12))

    def pack(self, **kwargs) -> None:
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.frame.grid(**kwargs)
