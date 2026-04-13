from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from typing import Callable, Iterable

from app.libs.ui_kit.components import DataTable


# ---- Notifier ---------------------------------------------------------------


class Notifier:
    @staticmethod
    def warn(message: str, title: str = "Notice") -> None:
        messagebox.showwarning(title, message)

    @staticmethod
    def info(message: str, title: str = "Info") -> None:
        messagebox.showinfo(title, message)

    @staticmethod
    def error(message: str, title: str = "Error") -> None:
        messagebox.showerror(title, message)


def validate_or_warn(
    errors: Iterable[str], notifier: Notifier, title: str = "Invalid data"
) -> bool:
    errs = list(errors)
    if errs:
        notifier.warn("\n".join(errs), title=title)
        return False
    return True


# ---- Selection helpers ------------------------------------------------------


@dataclass
class Choice:
    id: int
    label: str
    extra: dict | None = None


def map_choices(choices: list[Choice]) -> tuple[list[str], dict[str, Choice]]:
    labels = [c.label for c in choices]
    mapping = {c.label: c for c in choices}
    return labels, mapping


def resolve_selected(
    mapping: dict[str, Choice],
    selected_label: str,
    warn_if_missing: Callable[[str], None] | None = None,
) -> Choice | None:
    if not selected_label:
        if warn_if_missing:
            warn_if_missing("Select an option first.")
        return None
    choice = mapping.get(selected_label)
    if not choice and warn_if_missing:
        warn_if_missing("Selection is no longer available.")
    return choice


# ---- Table helpers ----------------------------------------------------------


def set_table_with_placeholder(
    table: DataTable, rows: list[tuple], placeholder: str
) -> None:
    if rows:
        table.set_rows(rows)
        return
    column_count = len(table["columns"])
    filler = ["" for _ in range(max(column_count - 1, 0))]
    table.set_rows([tuple([placeholder] + filler)])
