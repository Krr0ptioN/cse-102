from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.services.class_service import create_class, create_user, list_users
from app.services.roadmap_service import approve_roadmap, list_roadmaps_for_class
from app.services.team_service import (
    add_team_member,
    create_team,
    list_team_members,
    list_teams,
    update_team_principal,
)


class TeacherDashboard(tk.Frame):
    def __init__(self, master, db_path: str, on_back) -> None:
        super().__init__(master)
        self.db_path = db_path
        self.on_back = on_back
        self.class_id: int | None = None

        self._build()
        self._refresh_students()

    def _build(self) -> None:
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)
        tk.Button(header, text="Back", command=self.on_back).pack(side="left", padx=10)
        tk.Label(header, text="Teacher Dashboard", font=("Helvetica", 16, "bold")).pack(
            side="left", padx=10
        )

        content = tk.Frame(self)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_class_panel(content)
        self._build_student_panel(content)
        self._build_team_panel(content)
        self._build_roadmap_panel(content)

    def _build_class_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Class")
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text="Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame, text="Term").grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.class_name_entry = tk.Entry(frame, width=30)
        self.class_term_entry = tk.Entry(frame, width=20)
        self.class_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.class_term_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame, text="Create Class", command=self._create_class).grid(
            row=0, column=4, padx=5, pady=5
        )

        self.class_status = tk.Label(frame, text="No class selected")
        self.class_status.grid(row=1, column=0, columnspan=5, sticky="w", padx=5)

    def _build_student_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Students")
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text="Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame, text="Email").grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.student_name_entry = tk.Entry(frame, width=25)
        self.student_email_entry = tk.Entry(frame, width=30)
        self.student_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.student_email_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame, text="Add Student", command=self._add_student).grid(
            row=0, column=4, padx=5, pady=5
        )

        self.student_list = tk.Listbox(frame, height=4)
        self.student_list.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5, pady=5)

    def _build_team_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Teams")
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text="Team Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.team_name_entry = tk.Entry(frame, width=25)
        self.team_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(frame, text="Create Team", command=self._create_team).grid(
            row=0, column=2, padx=5, pady=5
        )

        tk.Label(frame, text="Teams").grid(row=1, column=0, sticky="w", padx=5)
        self.team_list = tk.Listbox(frame, height=4)
        self.team_list.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.team_list.bind("<<ListboxSelect>>", lambda _e: self._refresh_team_members())

        tk.Label(frame, text="Members").grid(row=1, column=2, sticky="w", padx=5)
        self.team_member_list = tk.Listbox(frame, height=4)
        self.team_member_list.grid(row=2, column=2, columnspan=2, sticky="ew", padx=5, pady=5)

        self.member_select = ttk.Combobox(frame, state="readonly")
        self.member_select.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        tk.Button(frame, text="Add Member", command=self._add_team_member).grid(
            row=3, column=2, padx=5, pady=5
        )

        self.principal_select = ttk.Combobox(frame, state="readonly")
        self.principal_select.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        tk.Button(frame, text="Set Principal", command=self._set_principal).grid(
            row=4, column=2, padx=5, pady=5
        )

    def _build_roadmap_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Roadmap Review")
        frame.pack(fill="both", expand=True, pady=5)

        columns = ("id", "team", "status")
        self.roadmap_tree = ttk.Treeview(frame, columns=columns, show="headings", height=5)
        for col in columns:
            self.roadmap_tree.heading(col, text=col.title())
        self.roadmap_tree.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Button(frame, text="Approve Selected", command=self._approve_roadmap).pack(
            pady=5
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
        item = self.roadmap_tree.selection()
        if not item:
            messagebox.showwarning("No roadmap", "Select a roadmap to approve.")
            return
        roadmap_id = int(self.roadmap_tree.item(item[0], "values")[0])
        approve_roadmap(self.db_path, roadmap_id)
        self._refresh_roadmaps()

    def _refresh_students(self) -> None:
        students = list_users(self.db_path, role="student")
        self.student_list.delete(0, tk.END)
        choices = []
        for student in students:
            self.student_list.insert(tk.END, f"{student['name']} ({student['email']})")
            choices.append(f"{student['id']} {student['name']}")
        self.member_select["values"] = choices
        self.principal_select["values"] = choices

    def _refresh_teams(self) -> None:
        self.team_list.delete(0, tk.END)
        if not self.class_id:
            return
        self.teams_cache = list_teams(self.db_path, self.class_id)
        for team in self.teams_cache:
            self.team_list.insert(tk.END, f"{team['id']} {team['name']}")

    def _refresh_team_members(self) -> None:
        self.team_member_list.delete(0, tk.END)
        team_id = self._selected_team_id()
        if not team_id:
            return
        members = list_team_members(self.db_path, team_id)
        for member in members:
            self.team_member_list.insert(
                tk.END, f"{member['name']} ({member['email']})"
            )

    def _refresh_roadmaps(self) -> None:
        for row in self.roadmap_tree.get_children():
            self.roadmap_tree.delete(row)
        if not self.class_id:
            return
        for roadmap in list_roadmaps_for_class(self.db_path, self.class_id):
            self.roadmap_tree.insert(
                "", "end", values=(roadmap["id"], roadmap["team"], roadmap["status"])
            )

    def _selected_team_id(self) -> int | None:
        selection = self.team_list.curselection()
        if not selection:
            return None
        entry = self.team_list.get(selection[0])
        return int(entry.split(" ", 1)[0])
