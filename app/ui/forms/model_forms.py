from __future__ import annotations

from app.ui.forms.base import Form
from app.ui.forms.fields import SelectField, TextAreaField, TextField
from app.ui.forms.validators import email, is_int, max_len, required


class ClassForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("name", "Class Name", [required, max_len(50)], width=28),
                TextField("term", "Term", [required, max_len(20)], width=18),
            ]
        )


class StudentForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("name", "Name", [required, max_len(50)], width=22),
                TextField("email", "Email", [required, email, max_len(80)], width=28),
            ]
        )


class TeamForm(Form):
    def __init__(self) -> None:
        super().__init__([TextField("name", "Team Name", [required, max_len(50)], width=22)])


class CommentForm(Form):
    def __init__(self) -> None:
        super().__init__([TextAreaField("text", "Comment", [required])])


class ApprovalNoteForm(Form):
    def __init__(self) -> None:
        super().__init__([TextAreaField("text", "Comment (optional)", [])])


class TaskForm(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                TextField("title", "Task Title", [required, max_len(80)], width=20),
                TextField("weight", "Weight", [required, is_int, max_len(3)], width=8),
            ]
        )


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
