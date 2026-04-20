from __future__ import annotations

import tkinter as tk

from libs.ui_kit import (
    Card, 
    SectionHeader, 
    StatCard, 
    CheckinListView, 
    TaskListView,
    Flex
)
from ui.shared.page import Page


class TeacherHomePage(Page):
    """Dashboard analytics / snapshots for the teacher."""

    title = "Dashboard"
    route = "dashboard"

    def on_mount(self) -> None:
        # Top Stats
        self.stats_container = tk.Frame(self, bg=self["bg"])
        self.stats_container.pack(fill="x", padx=12, pady=(12, 0))

        self._stats = {
            "Students": StatCard(self.stats_container, "Students", "0"),
            "Teams": StatCard(self.stats_container, "Teams", "0"),
            "Roadmaps": StatCard(self.stats_container, "Roadmaps", "0"),
        }
        for card in self._stats.values():
            card.pack(side="left", fill="x", expand=True, padx=4)

        # Main Grid for Activity
        self.grid_container = tk.Frame(self, bg=self["bg"])
        self.grid_container.pack(fill="both", expand=True, padx=8, pady=8)
        self.grid_container.columnconfigure(0, weight=1)
        self.grid_container.columnconfigure(1, weight=1)
        self.grid_container.rowconfigure(0, weight=1)

        # Recent Check-ins Column
        checkins_col = tk.Frame(self.grid_container, bg=self["bg"])
        checkins_col.grid(row=0, column=0, sticky="nsew", padx=4)
        
        SectionHeader(checkins_col, title="Recent Check-ins", subtitle="Latest team updates").pack(fill="x", padx=4)
        self.checkins_list = CheckinListView(checkins_col, on_checkin_select=self._view_checkin)
        self.checkins_list.pack(fill="both", expand=True, pady=4)

        # Recent Roadmaps/Tasks Column
        tasks_col = tk.Frame(self.grid_container, bg=self["bg"])
        tasks_col.grid(row=0, column=1, sticky="nsew", padx=4)
        
        SectionHeader(tasks_col, title="Active Tasks", subtitle="Tasks in progress across teams").pack(fill="x", padx=4)
        self.tasks_list = TaskListView(tasks_col, on_task_select=self._view_task)
        self.tasks_list.pack(fill="both", expand=True, pady=4)

    def on_show(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        class_id = self.dashboard.class_id
        services = self.dashboard.services
        
        if not class_id:
            self._clear_data()
            return
            
        students = services["class"].list_users(role="student")
        teams = services["team"].list_teams(class_id)
        roadmaps = services["roadmap"].list_roadmaps_for_class(class_id)
        
        self._stats["Students"].set_value(str(len(students)))
        self._stats["Teams"].set_value(str(len(teams)))
        self._stats["Roadmaps"].set_value(str(len(roadmaps)))

        # Recent check-ins
        checkins = services["checkin"].list_checkins_for_class(class_id)[:10]
        self.checkins_list.set_checkins([
            (c["id"], f"{c['week_start']} → {c['week_end']}", c["status"], f"{c['percent']}%", c["submitted_at"])
            for c in checkins
        ])

        # Active tasks across all teams in this class
        # (Assuming we have a service method or we aggregate)
        all_tasks = []
        for team in teams:
            roadmap = services["roadmap"].get_latest_roadmap(team["id"])
            if roadmap:
                team_tasks = services["task"].list_tasks_for_roadmap(roadmap["id"])
                # Filter for non-done tasks
                active = [t for t in team_tasks if t["status"] != "Done"]
                all_tasks.extend(active)
        
        all_tasks.sort(key=lambda x: x["id"], reverse=True)
        self.tasks_list.set_tasks([
            (t["id"], f"[{team['name']}] {t['title']}", t["status"], t["weight"])
            for t in all_tasks[:15]
        ])

    def _clear_data(self) -> None:
        for card in self._stats.values():
            card.set_value("0")
        self.checkins_list.set_checkins([])
        self.tasks_list.set_tasks([])

    def _view_checkin(self, checkin_id: int) -> None:
        # Switch to checkins page and select this one
        self.dashboard._navigate("checkins")
        self.dashboard.pages["checkins"]._on_checkin_selected(checkin_id)

    def _view_task(self, task_id: int) -> None:
        # Teacher dashboard doesn't have a dedicated "tasks" page yet (tasks are in roadmaps)
        # For now, just a placeholder or navigate to teams
        self.dashboard.log.info("Task clicked: %d", task_id)
