from __future__ import annotations

from app.libs.ui_kit.forms import Form, SelectField, TextAreaField, required


class CheckinForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                SelectField("status", "Status", [required]),
                TextAreaField("wins", "Wins", [required]),
                TextAreaField("risks", "Risks", [required]),
                TextAreaField("next_goal", "Next Goal", [required]),
                TextAreaField("help_needed", "Help Needed", []),
            ]
        )
