from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from libs.ui_kit import Modal, Section, add_modal_actions
from ui.shared.forms import CommentForm
from ui.teacher.forms import ApprovalNoteForm
from ui.teacher import CheckinsSection
from ui.shared.page import Page


class TeacherCheckinsPage(Page):
    title = "Check-ins"
    route = "checkins"

    def __init__(self, dashboard) -> None:
        super().__init__(dashboard)

    def on_mount(self) -> None:
        self.section = CheckinsSection(
            self,
            self._refresh_checkin_comments,
            self._add_checkin_comment,
            self._approve_checkin,
        )
        self.section.pack(fill="both", expand=True)

        # Drawer-like details for checkin summary
        self.details = Section(self, "Details")
        self.details.pack(fill="x", padx=12, pady=(0, 12))
        self.details_body = tk.Label(self.details.body, text="Select a check-in", bg=self.details.body["bg"])
        self.details_body.pack(anchor="w", padx=4, pady=4)

    def on_show(self) -> None:
        self._refresh_checkins()

    def _refresh_checkins(self) -> None:
        class_id = self.dashboard.class_id
        if not class_id:
            self.section.set_rows([])
            return
        checkins = self.dashboard.services["checkin"].list_checkins_for_class(class_id)
        rows = [
            (
                c["id"],
                c["team"],
                f"{c['week_start']} → {c['week_end']}",
                c["status"],
                f"{c['percent']}%",
                c["submitted_at"],
            )
            for c in checkins
        ]
        self.section.set_rows(rows)
        self._refresh_checkin_comments()
        self._show_checkin_details()

    def _selected_checkin_id(self) -> int | None:
        return self.section.selected_id()

    def _refresh_checkin_comments(self) -> None:
        checkin_id = self._selected_checkin_id()
        if not checkin_id:
            self.section.set_comment_rows([])
            return
        comments = self.dashboard.services["checkin"].list_checkin_comments(checkin_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.section.set_comment_rows(rows)
        self._show_checkin_details()

    def _add_checkin_comment(self) -> None:
        checkin_id = self._selected_checkin_id()
        if not checkin_id:
            messagebox.showwarning("No check-in", "Select a check-in first.")
            return
        modal = Modal(self, "Add Comment")
        form = CommentForm()
        form.render(modal.body)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            text = form.get_data()["text"]
            self.dashboard.services["checkin"].add_checkin_comment(
                checkin_id, "Teacher", text, "comment"
            )
            modal.destroy()
            self._refresh_checkin_comments()

        add_modal_actions(modal, save, confirm_text="Save")

    def _approve_checkin(self) -> None:
        checkin_id = self._selected_checkin_id()
        if not checkin_id:
            messagebox.showwarning("No check-in", "Select a check-in first.")
            return
        modal = Modal(self, "Approval Note")
        form = ApprovalNoteForm()
        form.render(modal.body)

        def save() -> None:
            note = form.get_data()["text"]
            if note:
                self.dashboard.services["checkin"].add_checkin_comment(
                    checkin_id, "Teacher", note, "approval"
                )
            if hasattr(self.dashboard.services["checkin"], "approve_checkin"):
                self.dashboard.services["checkin"].approve_checkin(checkin_id)
            modal.destroy()
            self._refresh_checkins()

        add_modal_actions(modal, save, confirm_text="Approve")

    def _show_checkin_details(self) -> None:
        checkin_id = self._selected_checkin_id()
        if not checkin_id:
            self.details_body.config(text="Select a check-in")
            return
        chk = self.dashboard.services["checkin"].get_checkin(checkin_id)
        if not chk:
            self.details_body.config(text="Select a check-in")
            return
        txt = (
            f"Check-in #{chk['id']}\n"
            f"Team ID: {chk['team_id']}\n"
            f"Week: {chk['week_start']} → {chk['week_end']}\n"
            f"Status: {chk['status']} ({chk['metrics_percent']}%)\n"
            f"Wins: {chk['wins']}\nRisks: {chk['risks']}\nNext: {chk['next_goal']}\n"
        )
        self.details_body.config(text=txt)
