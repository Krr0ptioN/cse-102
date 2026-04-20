from __future__ import annotations

import tkinter as tk
from libs.ui_kit import TaskListView, CommentThread, Label, Section, Button, Badge
from ui.student.pages.base import StudentSectionPage


class StudentTasksPage(StudentSectionPage):
    title = "Tasks"
    route = "tasks"
    subtitle = "Track implementation progress and updates."

    def on_mount(self) -> None:
        super().on_mount()
        self.list_view = TaskListView(self.body, on_task_select=self._on_task_selected)
        self.list_view.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self._refresh_tasks()

    def _refresh_tasks(self) -> None:
        roadmap_id = self.dashboard.current_roadmap_id
        if not roadmap_id:
            self.list_view.set_tasks([])
            return
            
        tasks = self.dashboard.services["task"].list_tasks_for_roadmap(roadmap_id)
        rows = [
            (t["id"], t["title"], t["status"], t["weight"])
            for t in tasks
        ]
        self.list_view.set_tasks(rows)

    def _on_task_selected(self, task_id: int) -> None:
        self.dashboard.slide_over.clear()
        
        task = self.dashboard.services["task"].get_task(task_id)
        if not task:
            return

        body = self.dashboard.slide_over.body
        bg = body["bg"]

        # Header
        Label(body, text=f"Task #{task_id}", weight="bold", size="lg").pack(anchor="w", pady=(0, 4))
        Label(body, text=task["title"], wraplength=280, justify="left").pack(anchor="w", pady=(0, 8))
        
        status_frame = tk.Frame(body, bg=bg)
        status_frame.pack(fill="x", pady=4)
        Label(status_frame, text="Status: ", variant="muted").pack(side="left")
        Badge(status_frame, text=task["status"], variant="outline").pack(side="left")
        
        # Details
        details_sec = Section(body, "Activity & Updates")
        details_sec.pack(fill="both", expand=True, pady=(12, 0))
        
        thread = CommentThread(details_sec.body, on_send=lambda txt: self._add_update(task_id, txt))
        thread.pack(fill="both", expand=True)
        
        updates = self.dashboard.services["task"].list_updates_for_task(task_id)
        thread.set_comments([(u["user"], u["text"], u["created_at"]) for u in updates])

        # Status update actions
        if self.dashboard.current_roadmap_status == "Approved":
            actions = self.dashboard.slide_over.actions
            Label(actions, text="Update Status", size="sm", variant="muted").pack(anchor="w", pady=(0, 4))
            btn_row = tk.Frame(actions, bg=bg)
            btn_row.pack(fill="x")
            
            for status in ["Todo", "In Progress", "Done"]:
                if status != task["status"]:
                    Button(
                        btn_row, 
                        text=status, 
                        size="xs", 
                        variant="secondary" if status != "Done" else "default",
                        command=lambda s=status: self._update_status(task_id, s)
                    ).pack(side="left", padx=2)

    def _add_update(self, task_id: int, text: str) -> None:
        self.dashboard.services["task"].add_update(task_id, self.dashboard.current_user.id, text)
        self._on_task_selected(task_id) # Refresh drawer

    def _update_status(self, task_id: int, status: str) -> None:
        self.dashboard.services["task"].update_task_status(task_id, status)
        self._refresh_tasks()
        self._on_task_selected(task_id)
