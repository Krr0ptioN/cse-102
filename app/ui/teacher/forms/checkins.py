from __future__ import annotations

from app.libs.ui_kit.forms import Form, TextAreaField


class ApprovalNoteForm(Form):
    def __init__(self) -> None:
        super().__init__([TextAreaField("text", "Comment (optional)", [])])
