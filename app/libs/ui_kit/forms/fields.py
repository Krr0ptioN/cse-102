from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import LabeledCombobox, LabeledEntry


class Field:
    def __init__(self, name: str, label: str, validators: list) -> None:
        self.name = name
        self.label = label
        self.validators = validators
        self.widget = None

    def render(self, master) -> tk.Widget:
        raise NotImplementedError

    def get(self) -> str:
        raise NotImplementedError

    def set(self, value: str) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        self.set("")


class TextField(Field):
    def __init__(self, name: str, label: str, validators: list, width: int = 24) -> None:
        super().__init__(name, label, validators)
        self.width = width
        self.entry = None

    def render(self, master) -> tk.Widget:
        field = LabeledEntry(master, self.label, width=self.width)
        self.entry = field.entry
        self.widget = field
        return field

    def get(self) -> str:
        return self.entry.get() if self.entry else ""

    def set(self, value: str) -> None:
        if not self.entry:
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class TextAreaField(Field):
    def __init__(self, name: str, label: str, validators: list, height: int = 4) -> None:
        super().__init__(name, label, validators)
        self.height = height
        self.text = None

    def render(self, master) -> tk.Widget:
        frame = tk.Frame(master)
        tk.Label(frame, text=self.label).pack(anchor="w")
        self.text = tk.Text(frame, height=self.height, width=40)
        self.text.pack(fill="x", pady=6)
        self.widget = frame
        return frame

    def get(self) -> str:
        return self.text.get("1.0", tk.END).strip() if self.text else ""

    def set(self, value: str) -> None:
        if not self.text:
            return
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", value)


class SelectField(Field):
    def __init__(self, name: str, label: str, validators: list, width: int = 24) -> None:
        super().__init__(name, label, validators)
        self.width = width
        self.combo = None

    def render(self, master) -> tk.Widget:
        field = LabeledCombobox(master, self.label, width=self.width)
        self.combo = field.combo
        self.widget = field
        return field

    def set_values(self, values: list[str]) -> None:
        if self.combo:
            self.combo["values"] = values

    def get(self) -> str:
        return self.combo.get() if self.combo else ""

    def set(self, value: str) -> None:
        if self.combo:
            self.combo.set(value)
