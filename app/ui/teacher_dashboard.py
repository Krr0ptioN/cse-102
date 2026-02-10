from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.services.class_service import (
    create_class,
    create_user,
    delete_user,
    list_users,
    update_user,
)
from app.services.roadmap_service import approve_roadmap, list_roadmaps_for_class
from app.services.task_service import list_tasks_for_class
from app.services.team_service import (
    add_team_member,
    create_team,
    delete_team,
    list_team_members,
    list_teams,
    update_team,
    update_team_principal,
)
from app.ui.charts import show_charts_window
from app.ui.components import AppShell, DataTable, DetailsDrawer, Modal, Section, StatCard


class TeacherDashboard(tk.Frame):
    def __init__(self, master, db_path: str, on_back) -> None:
        super().__init__(master)
        self.db_path = db_path
        self.on_back = on_back
        self.class_id: int | None = None
        self.teams_cache: list[dict] = []

        self.shell = AppShell(self, "Teacher Dashboard", on_back)
        self.shell.pack(fill="both", expand=True)

        self._build_layout()
        self._refresh_students()
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _build_layout(self) -> None:
        content = self.shell.content
        content.grid_rowconfigure(1, weight=0)
        content.grid_rowconfigure(2, weight=1)
        content.grid_rowconfigure(3, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=0, minsize=260)

        self.stats_row = tk.Frame(content)
        self.stats_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=8)
        self.stats_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_students = StatCard(self.stats_row, "Students", "0")
        self.stat_students.grid(row=0, column=0, padx=8, sticky="ew")
        self.stat_teams = StatCard(self.stats_row, "Teams", "0")
        self.stat_teams.grid(row=0, column=1, padx=8, sticky="ew")
        self.stat_roadmaps = StatCard(self.stats_row, "Roadmaps", "0")
        self.stat_roadmaps.grid(row=0, column=2, padx=8, sticky="ew")

        self.class_section = Section(content, "Class Setup")
        self.class_section.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        self._build_class_panel(self.class_section.body)

        self.student_section = Section(content, "Student Roster")
        self.student_section.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self._build_student_panel(self.student_section.body)

        self.team_section = Section(content, "Teams")
        self.team_section.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=8, pady=8)
        self._build_team_panel(self.team_section.body)

        self.roadmap_section = Section(content, "Roadmap Review")
        self.roadmap_section.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self._build_roadmap_panel(self.roadmap_section.body)

        self.drawer = DetailsDrawer(content, "Details")
        self.drawer.grid(row=1, column=2, rowspan=3, sticky="nsew", padx=8, pady=8)

        tk.Button(self.shell.topbar.actions, text="View Charts", command=self._show_charts).pack(
            side="left", padx=6
        )

    def _build_class_panel(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Class Name").grid(row=0, column=0, sticky="w", pady=4)
        tk.Label(parent, text="Term").grid(row=0, column=2, sticky="w", pady=4)

        self.class_name_entry = tk.Entry(parent, width=28)
        self.class_term_entry = tk.Entry(parent, width=18)
        self.class_name_entry.grid(row=1, column=0, padx=4, pady=4)
        self.class_term_entry.grid(row=1, column=2, padx=4, pady=4)

        tk.Button(parent, text="Create Class", command=self._create_class).grid(
            row=1, column=3, padx=6, pady=4
        )

        self.class_status = tk.Label(parent, text="No class selected")
        self.class_status.grid(row=2, column=0, columnspan=4, sticky="w")

    def _build_student_panel(self, parent: tk.Frame) -> None:
        form = tk.Frame(parent)
        form.pack(fill="x", pady=6)

        tk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Email").grid(row=0, column=2, sticky="w")

        self.student_name_entry = tk.Entry(form, width=22)
        self.student_email_entry = tk.Entry(form, width=28)
        self.student_name_entry.grid(row=1, column=0, padx=4, pady=4)
        self.student_email_entry.grid(row=1, column=2, padx=4, pady=4)

        tk.Button(form, text="Add Student", command=self._add_student).grid(
            row=1, column=3, padx=6, pady=4
        )

        toolbar = tk.Frame(parent)
        toolbar.pack(fill="x", pady=6)
        tk.Button(toolbar, text="Edit", command=self._edit_student).pack(side="left", padx=4)
        tk.Button(toolbar, text="Delete", command=self._delete_student).pack(side="left", padx=4)

        self.student_table = DataTable(parent, ["Id", "Name", "Email"], height=6)
        self.student_table.pack(fill="both", expand=True, pady=6)
        self.student_table.bind("<<TreeviewSelect>>", lambda _e: self._show_student_details())

    def _build_team_panel(self, parent: tk.Frame) -> None:
        form = tk.Frame(parent)
        form.pack(fill="x", pady=6)

        tk.Label(form, text="Team Name").grid(row=0, column=0, sticky="w")
        self.team_name_entry = tk.Entry(form, width=22)
        self.team_name_entry.grid(row=1, column=0, padx=4, pady=4)
        tk.Button(form, text="Create Team", command=self._create_team).grid(
            row=1, column=1, padx=6
        )

        tables = tk.Frame(parent)
        tables.pack(fill="both", expand=True)
        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)

        self.team_table = DataTable(tables, ["Id", "Team", "Principal"], height=6)
        self.team_table.grid(row=0, column=0, sticky="nsew", padx=4, pady=6)
        self.team_table.bind("<<TreeviewSelect>>", lambda _e: self._refresh_team_members())

        self.team_member_table = DataTable(tables, ["Id", "Member", "Email"], height=6)
        self.team_member_table.grid(row=0, column=1, sticky="nsew", padx=4, pady=6)

        actions = tk.Frame(parent)
        actions.pack(fill="x", pady=6)

        self.member_select = ttk.Combobox(actions, state="readonly")
        self.member_select.pack(side="left", padx=4)
        tk.Button(actions, text="Add Member", command=self._add_team_member).pack(
            side="left", padx=4
        )

        self.principal_select = ttk.Combobox(actions, state="readonly")
        self.principal_select.pack(side="left", padx=4)
        tk.Button(actions, text="Set Principal", command=self._set_principal).pack(
            side="left", padx=4
        )

        tk.Button(actions, text="Edit Team", command=self._edit_team).pack(side="left", padx=4)
        tk.Button(actions, text="Delete Team", command=self._delete_team).pack(side="left", padx=4)

    def _build_roadmap_panel(self, parent: tk.Frame) -> None:
        self.roadmap_table = DataTable(parent, ["Id", "Team", "Status"], height=6)
        self.roadmap_table.pack(fill="both", expand=True, pady=6)

        tk.Button(parent, text="Approve Selected", command=self._approve_roadmap).pack(
            anchor="e", pady=4
        )

    def _create_class(self) -> None:
        name = self.class_name_entry.get().strip()
        term = self.class_term_entry.get().strip()
        if not name or not term:
            messagebox.showwarning("Missing data", "Enter a class name and term.")
            return
        self.class_id = create_class(self.db_path, name, term)
        self.class_status.config(text=f"Active class: {name} ({term})")
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _add_student(self) -> None:
        name = self.student_name_entry.get().strip()
        email = self.student_email_entry.get().strip()
        if not name or not email:
            messagebox.showwarning("Missing data", "Enter student name and email.")
            return
        create_user(self.db_path, name, email, "student")
        self.student_name_entry.delete(0, tk.END)
        self.student_email_entry.delete(0, tk.END)
        self._refresh_students()
        self._refresh_stats()

    def _create_team(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return
        name = self.team_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing data", "Enter a team name.")
            return
        create_team(self.db_path, self.class_id, name, None)
        self.team_name_entry.delete(0, tk.END)
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _add_team_member(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.member_select.get()
        if not selection:
            messagebox.showwarning("No student", "Select a student to add.")
            return
        user_id = int(selection.split(" ", 1)[0])
        add_team_member(self.db_path, team_id, user_id)
        self._refresh_team_members()

    def _set_principal(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.principal_select.get()
        if not selection:
            messagebox.showwarning("No student", "Select a principal student.")
            return
        user_id = int(selection.split(" ", 1)[0])
        update_team_principal(self.db_path, team_id, user_id)
        self._refresh_teams()

    def _approve_roadmap(self) -> None:
        item = self.roadmap_table.selection()
        if not item:
            messagebox.showwarning("No roadmap", "Select a roadmap to approve.")
            return
        roadmap_id = int(self.roadmap_table.item(item[0], "values")[0])
        approve_roadmap(self.db_path, roadmap_id)
        self._refresh_roadmaps()
        self._refresh_stats()

    def _refresh_students(self) -> None:
        students = list_users(self.db_path, role="student")
        rows = [(s["id"], s["name"], s["email"]) for s in students]
        self.student_table.set_rows(rows)
        choices = [f"{s['id']} {s['name']}" for s in students]
        self.member_select["values"] = choices
        self.principal_select["values"] = choices

    def _refresh_teams(self) -> None:
        if not self.class_id:
            self.team_table.set_rows([])
            return
        self.teams_cache = list_teams(self.db_path, self.class_id)
        rows = []
        for team in self.teams_cache:
            principal = team["principal_user_id"] or "-"
            rows.append((team["id"], team["name"], principal))
        self.team_table.set_rows(rows)
        self._show_team_details()

    def _refresh_team_members(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.team_member_table.set_rows([])
            return
        members = list_team_members(self.db_path, team_id)
        rows = [(m["id"], m["name"], m["email"]) for m in members]
        self.team_member_table.set_rows(rows)
        self._show_team_details()

    def _refresh_roadmaps(self) -> None:
        if not self.class_id:
            self.roadmap_table.set_rows([])
            return
        roadmaps = list_roadmaps_for_class(self.db_path, self.class_id)
        rows = [(r["id"], r["team"], r["status"]) for r in roadmaps]
        self.roadmap_table.set_rows(rows)

    def _refresh_stats(self) -> None:
        students = list_users(self.db_path, role="student")
        teams = list_teams(self.db_path, self.class_id) if self.class_id else []
        roadmaps = list_roadmaps_for_class(self.db_path, self.class_id) if self.class_id else []
        self.stat_students.set_value(str(len(students)))
        self.stat_teams.set_value(str(len(teams)))
        self.stat_roadmaps.set_value(str(len(roadmaps)))

    def _show_charts(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return
        tasks = list_tasks_for_class(self.db_path, self.class_id)
        show_charts_window(self, "Class Charts", tasks)

    def _selected_team_id(self) -> int | None:
        selection = self.team_table.selection()
        if not selection:
            return None
        return int(self.team_table.item(selection[0], "values")[0])

    def _selected_student_id(self) -> int | None:
        selection = self.student_table.selection()
        if not selection:
            return None
        return int(self.student_table.item(selection[0], "values")[0])

    def _show_student_details(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            return
        row = self.student_table.item(self.student_table.selection()[0], "values")
        self.drawer.clear()
        tk.Label(self.drawer.body, text=f"Student #{row[0]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Name: {row[1]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Email: {row[2]}").pack(anchor="w")
        tk.Button(self.drawer.actions, text="Edit", command=self._edit_student).pack(
            side="left", padx=4
        )
        tk.Button(self.drawer.actions, text="Delete", command=self._delete_student).pack(
            side="left", padx=4
        )

    def _show_team_details(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            return
        row = self.team_table.item(self.team_table.selection()[0], "values")
        self.drawer.clear()
        tk.Label(self.drawer.body, text=f"Team #{row[0]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Name: {row[1]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Principal: {row[2]}").pack(anchor="w")
        tk.Button(self.drawer.actions, text="Edit", command=self._edit_team).pack(
            side="left", padx=4
        )
        tk.Button(self.drawer.actions, text="Delete", command=self._delete_team).pack(
            side="left", padx=4
        )

    def _edit_student(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            messagebox.showwarning("No student", "Select a student first.")
            return
        row = self.student_table.item(self.student_table.selection()[0], "values")
        modal = Modal(self, "Edit Student")
        tk.Label(modal.body, text="Name").grid(row=0, column=0, sticky="w")
        tk.Label(modal.body, text="Email").grid(row=1, column=0, sticky="w")
        name_entry = tk.Entry(modal.body, width=24)
        email_entry = tk.Entry(modal.body, width=28)
        name_entry.grid(row=0, column=1, padx=6, pady=4)
        email_entry.grid(row=1, column=1, padx=6, pady=4)
        name_entry.insert(0, row[1])
        email_entry.insert(0, row[2])

        def save() -> None:
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            if not name or not email:
                messagebox.showwarning("Missing data", "Enter a name and email.")
                return
            update_user(self.db_path, student_id, name, email)
            modal.destroy()
            self._refresh_students()
            self._refresh_stats()

        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_student(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            messagebox.showwarning("No student", "Select a student first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this student?"):
            return
        delete_user(self.db_path, student_id)
        self._refresh_students()
        self._refresh_team_members()
        self._refresh_stats()

    def _edit_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        row = self.team_table.item(self.team_table.selection()[0], "values")
        modal = Modal(self, "Edit Team")
        tk.Label(modal.body, text="Team Name").grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(modal.body, width=24)
        name_entry.grid(row=0, column=1, padx=6, pady=4)
        name_entry.insert(0, row[1])

        def save() -> None:
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing data", "Enter a team name.")
                return
            update_team(self.db_path, team_id, name)
            modal.destroy()
            self._refresh_teams()

        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this team?"):
            return
        delete_team(self.db_path, team_id)
        self._refresh_teams()
        self._refresh_team_members()
        self._refresh_roadmaps()
        self._refresh_stats()
