from __future__ import annotations

from app.libs.ui_kit.forms import Form, TextField, max_len, required


class ClassForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("name", "Class Name", [required, max_len(50)], width=28),
                TextField("term", "Term", [required, max_len(20)], width=18),
            ]
        )
