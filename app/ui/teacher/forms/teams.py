from __future__ import annotations

from app.libs.ui_kit.forms import Form, TextField, max_len, required


class TeamForm(Form):
    def __init__(self) -> None:
        super().__init__([TextField("name", "Team Name", [required, max_len(50)], width=22)])
