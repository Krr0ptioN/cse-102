from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from ui.teacher import RoadmapReviewSection
from libs.ui_kit import Modal, add_modal_actions, CommentThread, Section, Button, Label
from ui.shared.page import Page


class TeacherRoadmapsPage(Page):
    title = "Roadmaps"
    route = "roadmaps"

    def on_mount(self) -> None:
        self.roadmap_section = RoadmapReviewSection(
            self,
            self._add_comment_placeholder, # Legacy callback
            self._approve_roadmap,
            self._on_roadmap_selected,
        )
        self.roadmap_section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self._refresh_roadmaps()

    def _selected_roadmap_id(self) -> int | None:
        return self.roadmap_section.selected_roadmap_id()

    def _refresh_roadmaps(self) -> None:
        class_id = self.dashboard.class_id
        if not class_id:
            self.roadmap_section.set_roadmap_rows([])
            return
        roadmaps = self.dashboard.services["roadmap"].list_roadmaps_for_class(class_id)
        rows = [
            (r["id"], r["team"], r.get("principal") or "-", r["status"])
            for r in roadmaps
        ]
        self.roadmap_section.set_roadmap_rows(rows)

    def _on_roadmap_selected(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            self.dashboard.slide_over.clear()
            self.roadmap_section.set_phase_data([])
            return
            
        # Fetch phases for the central view
        phases = self.dashboard.services["roadmap"].list_phases_with_tasks(roadmap_id)
        self.roadmap_section.set_phase_data(phases)
            
        self.dashboard.slide_over.clear()
        body = self.dashboard.slide_over.body
        
        Label(body, text=f"Roadmap Review", weight="bold", size="lg").pack(anchor="w", pady=(0, 4))
        Label(body, text=f"ID: #{roadmap_id}", variant="muted").pack(anchor="w", pady=(0, 12))

        # Comment Thread
        comment_sec = Section(body, "Review Discussion")
        comment_sec.pack(fill="both", expand=True)
        
        thread = CommentThread(comment_sec.body, on_send=lambda txt: self._add_comment(roadmap_id, txt))
        thread.pack(fill="both", expand=True)
        
        comments = self.dashboard.services["roadmap"].list_roadmap_comments(roadmap_id)
        thread.set_comments([(c["author"], c["text"], c["created_at"]) for c in comments])
        
        # Approval action
        roadmaps = self.dashboard.services["roadmap"].list_roadmaps_for_class(self.dashboard.class_id)
        current = next((r for r in roadmaps if r["id"] == roadmap_id), None)
        
        if current and current["status"] == "Submitted":
            Button(
                self.dashboard.slide_over.actions,
                text="Approve Roadmap",
                command=lambda: self._approve_roadmap_action(roadmap_id)
            ).pack(fill="x")

    def _add_comment(self, roadmap_id: int, text: str) -> None:
        self.dashboard.services["roadmap"].add_roadmap_comment(
            roadmap_id, "Teacher", text, "comment"
        )
        self._on_roadmap_selected()

    def _add_comment_placeholder(self) -> None:
        # Legacy callback for internal section wiring
        pass

    def _approve_roadmap_action(self, roadmap_id: int) -> None:
        self.dashboard.services["roadmap"].approve_roadmap(roadmap_id)
        self._refresh_roadmaps()
        self._on_roadmap_selected()

    def _approve_roadmap(self) -> None:
        # Legacy button callback from main section
        roadmap_id = self._selected_roadmap_id()
        if roadmap_id:
            self._approve_roadmap_action(roadmap_id)
