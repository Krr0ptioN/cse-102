from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.ui.teacher import RoadmapReviewSection
from app.ui.forms import CommentForm
from app.ui.components import Modal, add_modal_actions


class TeacherRoadmapsPage(tk.Frame):
    title = "Roadmaps"

    def __init__(self, master, services: dict, class_id: int | None) -> None:
        colors_bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=colors_bg)
        self.services = services
        self.class_id = class_id

        self._build()
        self._refresh_roadmaps()

    def _build(self) -> None:
        self.roadmap_section = RoadmapReviewSection(
            self,
            self._add_comment,
            self._approve_roadmap,
            self._refresh_comments,
        )
        self.roadmap_section.pack(fill="both", expand=True)

    def _selected_roadmap_id(self) -> int | None:
        return self.roadmap_section.selected_roadmap_id()

    def _refresh_roadmaps(self) -> None:
        if not self.class_id:
            self.roadmap_section.set_roadmap_rows([])
            return
        roadmaps = self.services["roadmap"].list_roadmaps_for_class(self.class_id)
        rows = [
            (r["id"], r["team"], r.get("principal") or "-", r["status"])
            for r in roadmaps
        ]
        self.roadmap_section.set_roadmap_rows(rows)
        self._refresh_comments()

    def _refresh_comments(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            self.roadmap_section.set_comment_rows([])
            return
        comments = self.services["roadmap"].list_roadmap_comments(roadmap_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.roadmap_section.set_comment_rows(rows)

    def _add_comment(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            messagebox.showwarning("No roadmap", "Select a roadmap first.")
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
            self.services["roadmap"].add_roadmap_comment(
                roadmap_id, "Teacher", text, "comment"
            )
            modal.destroy()
            self._refresh_comments()

        add_modal_actions(modal, save, confirm_text="Save")

    def _approve_roadmap(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            messagebox.showwarning("No roadmap", "Select a roadmap first.")
            return
        self.services["roadmap"].approve_roadmap(roadmap_id)
        self._refresh_roadmaps()
