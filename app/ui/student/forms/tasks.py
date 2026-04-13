from __future__ import annotations

from app.libs.ui_kit.forms import Form, TextField, is_int, max_len, required


class TaskForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("title", "Task Title", [required, max_len(80)], width=20),
                TextField("weight", "Weight", [required, is_int, max_len(3)], width=8),
            ]
        )
