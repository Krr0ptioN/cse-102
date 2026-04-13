from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.design_system.component_tokens import button_variants
from app.libs.ui_kit.components.actions import add_modal_actions
from app.libs.ui_kit.components.modals import Modal
from app.libs.ui_kit.components.primitives.button import Button
from app.libs.ui_kit.components.primitives.input import Input
from app.libs.ui_kit.components.primitives.label import Label
from app.libs.ui_kit.components.primitives.select import Select
from app.libs.ui_kit.theme import palette


class FormDialog:
    """Composable dialog helper for small CRUD forms."""

    def __init__(
        self,
        master,
        *,
        title: str,
        subtitle: str | None = None,
    ) -> None:
        self.modal = Modal(master, title)
        self.body = self.modal.body
        self._variables: dict[str, tk.StringVar] = {}

        if subtitle:
            tk.Label(
                self.body,
                text=subtitle,
                anchor="w",
                justify="left",
                wraplength=540,
                bg=self.body["bg"],
            ).pack(fill="x", pady=(0, 8))

    def _field_shell(self, label: str) -> tk.Frame:
        shell = tk.Frame(self.body, bg=self.body["bg"])
        shell.pack(fill="x", pady=(0, 8))
        Label(shell, text=label, variant="muted").pack(anchor="w", pady=(0, 4))
        return shell

    def add_text(self, name: str, *, label: str, width: int = 30) -> tk.StringVar:
        variable = tk.StringVar(value="")
        shell = self._field_shell(label)
        Input(shell, width=width, textvariable=variable).pack(fill="x")
        self._variables[name] = variable
        return variable

    def add_select(
        self,
        name: str,
        *,
        label: str,
        values: list[str],
        width: int = 30,
    ) -> tk.StringVar:
        default = values[0] if values else ""
        variable = tk.StringVar(value=default)
        shell = self._field_shell(label)
        Select(shell, values=values, variable=variable, width=width).pack(fill="x")
        self._variables[name] = variable
        return variable

    def value(self, name: str) -> str:
        variable = self._variables.get(name)
        return variable.get().strip() if variable else ""

    def add_actions(self, on_confirm, *, confirm_text: str = "Save") -> None:
        add_modal_actions(self.modal, on_confirm, confirm_text=confirm_text)

    def destroy(self) -> None:
        self.modal.destroy()


class ToggleSelectionList(tk.Frame):
    """Selectable rows with per-row add/remove toggle action."""

    def __init__(self, master, rows: list[tuple[int, str]]) -> None:
        colors = palette()
        bg = master["bg"] if isinstance(master, tk.BaseWidget) else colors["panel"]
        super().__init__(master, bg=bg)
        self._selected_ids: set[int] = set()
        self._buttons: dict[int, tk.Widget] = {}
        self._rows = rows
        self._build()

    def _build(self) -> None:
        for user_id, label in self._rows:
            row = tk.Frame(self, bg=self["bg"])
            row.pack(fill="x", pady=2)

            tk.Label(row, text=label, anchor="w", bg=self["bg"]).pack(
                side="left", fill="x", expand=True
            )

            button = Button(
                row,
                text="Add",
                variant="secondary",
                size="sm",
                command=lambda uid=user_id: self._toggle(uid),
            )
            button.pack(side="right")
            self._buttons[user_id] = button

    def _toggle(self, user_id: int) -> None:
        if user_id in self._selected_ids:
            self._selected_ids.remove(user_id)
            self._buttons[user_id].configure(text="Add")
            self._set_button_variant(self._buttons[user_id], variant="secondary")
            return

        self._selected_ids.add(user_id)
        self._buttons[user_id].configure(text="✕ Remove")
        self._set_button_variant(self._buttons[user_id], variant="danger")

    @staticmethod
    def _set_button_variant(button, *, variant: str) -> None:
        tokens = button_variants()[variant]
        if variant == "danger":
            try:
                button.configure(
                    bg=tokens.bg,
                    fg=tokens.fg,
                    activebackground=tokens.hover,
                    activeforeground=tokens.fg,
                    highlightbackground=tokens.border,
                )
            except tk.TclError:
                button.configure(
                    fg_color=tokens.bg,
                    text_color=tokens.fg,
                    hover_color=tokens.hover,
                    border_color=tokens.border,
                )
        else:
            try:
                button.configure(
                    bg=tokens.bg,
                    fg=tokens.fg,
                    activebackground=tokens.hover,
                    activeforeground=tokens.fg,
                    highlightbackground=tokens.border,
                )
            except tk.TclError:
                button.configure(
                    fg_color=tokens.bg,
                    text_color=tokens.fg,
                    hover_color=tokens.hover,
                    border_color=tokens.border,
                )

    def selected_ids(self) -> list[int]:
        return sorted(self._selected_ids)
