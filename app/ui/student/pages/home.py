from __future__ import annotations

import tkinter as tk
from libs.ui_kit import SectionHeader, TaskListView, CheckinListView, StatCard, Card, palette
from ui.shared import Page, TaskDistributionChart


class StudentHomePage(Page):
    title = "Overview"
    route = "overview"

    def on_mount(self) -> None:
        # Top Stats
        self.stats_container = tk.Frame(self, bg=self["bg"])
        self.stats_container.pack(fill="x", padx=12, pady=(12, 0))

        self._stats = {
            "Status": StatCard(self.stats_container, "Roadmap Status", "None"),
            "Completed": StatCard(self.stats_container, "Tasks Done", "0"),
        }
        for card in self._stats.values():
            card.pack(side="left", fill="x", expand=True, padx=4)

        # Main Grid
        self.grid_container = tk.Frame(self, bg=self["bg"])
        self.grid_container.pack(fill="both", expand=True, padx=8, pady=8)
        self.grid_container.columnconfigure(0, weight=2) # Tasks
        self.grid_container.columnconfigure(1, weight=2) # Check-ins
        self.grid_container.columnconfigure(2, weight=1) # Chart
        self.grid_container.rowconfigure(0, weight=1)

        # Tasks Column
        tasks_col = tk.Frame(self.grid_container, bg=self["bg"])
        tasks_col.grid(row=0, column=0, sticky="nsew", padx=4)
        
        SectionHeader(tasks_col, title="My Active Tasks", subtitle="Remaining work").pack(fill="x", padx=4)
        self.tasks_list = TaskListView(tasks_col, on_task_select=self._view_task)
        self.tasks_list.pack(fill="both", expand=True, pady=4)

        # Check-ins Column
        checkins_col = tk.Frame(self.grid_container, bg=self["bg"])
        checkins_col.grid(row=0, column=1, sticky="nsew", padx=4)
        
        SectionHeader(checkins_col, title="Team Check-ins", subtitle="Recent history").pack(fill="x", padx=4)
        self.checkins_list = CheckinListView(checkins_col, on_checkin_select=self._view_checkin)
        self.checkins_list.pack(fill="both", expand=True, pady=4)

        # Chart Column
        chart_col = tk.Frame(self.grid_container, bg=self["bg"])
        chart_col.grid(row=0, column=2, sticky="nsew", padx=4)
        
        SectionHeader(chart_col, title="Distribution").pack(fill="x", padx=4)
        self.chart_card = Card(chart_col)
        self.chart_card.pack(fill="both", expand=True, pady=4)
        
        # Using the encapsulated Chart Widget
        self.task_chart = TaskDistributionChart(self.chart_card)
        self.task_chart.pack(fill="both", expand=True, padx=8, pady=8)

    def on_show(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        d = self.dashboard
        team_id = d.current_team_id
        roadmap_id = d.current_roadmap_id
        services = d.services
        
        if not team_id:
            self._clear_data()
            return
            
        # Stats
        self._stats["Status"].set_value(d.current_roadmap_status or "None")
        
        # Tasks
        tasks = []
        if roadmap_id:
            tasks = services["task"].list_tasks_for_roadmap(roadmap_id)
            done_count = len([t for t in tasks if t["status"] == "Done"])
            self._stats["Completed"].set_value(str(done_count))
            
            active_tasks = [t for t in tasks if t["status"] != "Done"]
            self.tasks_list.set_tasks([
                (t["id"], t["title"], t["status"], t["weight"])
                for t in active_tasks[:10]
            ])
        else:
            self._stats["Completed"].set_value("0")
            self.tasks_list.set_tasks([])

        # Check-ins
        checkins = services["checkin"].list_checkins_for_team(team_id)[:5]
        self.checkins_list.set_checkins([
            (c["id"], f"{c['week_start']} → {c['week_end']}", c["status"], f"{c.get('metrics_percent', 0)}%", c["submitted_at"])
            for c in checkins
        ])

        # Update the encapsulated Chart
        self.task_chart.update_data(tasks)

    def _clear_data(self) -> None:
        self._stats["Status"].set_value("No Team")
        self._stats["Completed"].set_value("0")
        self.tasks_list.set_tasks([])
        self.checkins_list.set_checkins([])
        self.task_chart.update_data([])

    def _view_task(self, task_id: int) -> None:
        self.dashboard._navigate("tasks")
        self.dashboard.pages["tasks"]._on_task_selected(task_id)

    def _view_checkin(self, checkin_id: int) -> None:
        self.dashboard._navigate("checkins")
        self.dashboard.pages["checkins"]._on_checkin_selected(checkin_id)
