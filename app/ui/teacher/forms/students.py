from __future__ import annotations

from libs.ui_kit.forms import Form, TextField, email, max_len, required


class StudentForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("name", "Name", [required, max_len(50)], width=22),
                TextField("email", "Email", [required, email, max_len(80)], width=28),
            ]
        )
