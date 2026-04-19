from __future__ import annotations

from libs.ui_kit.forms import Field


class Form:
    def __init__(self, fields: list[Field]) -> None:
        self.fields = fields

    def render(self, master, columns: int = 1, start_row: int = 0, start_col: int = 0) -> None:
        for idx, field in enumerate(self.fields):
            widget = field.render(master)
            row = start_row + (idx // columns)
            col = start_col + (idx % columns)
            widget.grid(row=row, column=col, sticky="w", padx=4, pady=4)

    def get_data(self) -> dict:
        return {field.name: field.get() for field in self.fields}

    def set_data(self, data: dict) -> None:
        for field in self.fields:
            if field.name in data:
                field.set(str(data[field.name]))

    def get_field(self, name: str) -> Field | None:
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def clear(self) -> None:
        for field in self.fields:
            field.clear()

    def validate(self) -> list[str]:
        errors: list[str] = []
        for field in self.fields:
            value = field.get()
            for validator in field.validators:
                result = validator(value)
                if result:
                    errors.append(f"{field.label}: {result}")
        return errors
