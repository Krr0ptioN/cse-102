from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from libs.ui_kit import (
    FormDialog, 
    ToggleSelectionList, 
    TeamListView, 
    MemberListView,
    DataTable, 
    Section, 
    Button, 
    Label,
    ButtonBar,
    Flex,
    palette
)
from ui.shared.page import Page


class TeacherTeamsPage(Page):
    title = "Teams"
    route = "teams"

    def __init__(self, dashboard) -> None:
        self._students: list[dict] = []
        self._member_rows: list[tuple] = []
        super().__init__(dashboard)

    def on_mount(self) -> None:
        # Header with create action
        self.header = tk.Frame(self, bg=self["bg"])
        self.header.pack(fill="x", padx=12, pady=12)
        
        tk.Label(
            self.header, 
            text="Team Management", 
            font=("TkDefaultFont", 16, "bold"),
            bg=self["bg"],
            fg=palette()["text"]
        ).pack(side="left")
        
        Button(self.header, text="Create Team", command=self._team_create_modal, size="sm").pack(side="right")

        # Main List
        self.list_view = TeamListView(self, on_team_select=self._on_team_selected)
        self.list_view.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def on_show(self) -> None:
        self._refresh_students()
        self._refresh_teams()

    def _refresh_students(self) -> None:
        self._students = self.dashboard.services["class"].list_users(role="student")

    def _refresh_teams(self) -> None:
        class_id = self.dashboard.class_id
        if not class_id:
            self.list_view.set_teams([])
            return
        teams = self.dashboard.services["team"].list_teams(class_id)
        rows = []
        for team in teams:
            principal = team["principal_name"] or "-"
            rows.append((team["id"], team["name"], principal))
        self.list_view.set_teams(rows)

    def _on_team_selected(self, team_id: int) -> None:
        self.dashboard.slide_over.clear()
        self.dashboard.slide_over.config(width=380) # Good width for details
        
        team = self.dashboard.services["team"].get_team(team_id)
        if not team:
            return

        body = self.dashboard.slide_over.body
        bg = body["bg"]

        # Header
        Label(body, text=team["name"], weight="bold", size="lg").pack(anchor="w", pady=(0, 4))
        Label(body, text=f"Team ID: #{team_id}", variant="muted").pack(anchor="w", pady=(0, 12))

        # Members Section
        members_sec = Section(body, "Team Members")
        members_sec.pack(fill="x", pady=4)
        
        members = self.dashboard.services["team"].list_team_members(team_id)
        self._member_rows = [(m["id"], m["name"], m["email"], m["role"]) for m in members]
        
        member_list = MemberListView(members_sec.body, bg=members_sec.body["bg"])
        member_list.pack(fill="x", pady=4)
        member_list.set_members([(m["name"], m["email"], m["role"]) for m in members])

        # Invites Section
        invites = self.dashboard.services["team"].list_invitations_for_team(team_id)
        if invites:
            invites_sec = Section(body, "Pending Invitations")
            invites_sec.pack(fill="x", pady=8)
            
            invite_table = DataTable(invites_sec.body, ["Student", "Status"], height=len(invites))
            invite_table.pack(fill="x")
            invite_table.set_rows([(i["user"], i["status"]) for i in invites])

        # Actions
        actions = self.dashboard.slide_over.actions
        Label(actions, text="Manage Team", size="sm", variant="muted").pack(anchor="w", pady=(0, 4))
        
        btn_bar = tk.Frame(actions, bg=bg)
        btn_bar.pack(fill="x")
        
        Button(btn_bar, text="Add Member", size="xs", command=lambda: self._add_team_member(team_id)).pack(side="left", padx=2)
        Button(btn_bar, text="Invite", size="xs", variant="outline", command=lambda: self._send_invite(team_id)).pack(side="left", padx=2)
        Button(btn_bar, text="Set Principal", size="xs", variant="outline", command=lambda: self._set_principal(team_id)).pack(side="left", padx=2)
        
        danger_row = tk.Frame(actions, bg=bg)
        danger_row.pack(fill="x", pady=(12, 0))
        Button(danger_row, text="Delete Team", size="xs", variant="danger", command=lambda: self._delete_team(team_id)).pack(side="right")

    # --- dialog option builders
    def _student_options(self) -> tuple[list[str], dict[str, int]]:
        options: list[str] = []
        mapping: dict[str, int] = {}
        for student in self._students:
            label = f"{student['name']} ({student['email']})"
            options.append(label)
            mapping[label] = int(student["id"])
        return options, mapping

    # --- actions
    def _team_create_modal(self) -> None:
        class_id = self.dashboard.class_id
        if not class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return

        dialog = FormDialog(
            self,
            title="Create Team",
            subtitle="Create a new team and optionally add students.",
        )
        dialog.add_text("name", label="Team Name")

        student_rows = [
            (int(student["id"]), f"{student['name']} ({student['email']})")
            for student in self._students
        ]
        picker = ToggleSelectionList(dialog.body, student_rows)
        picker.pack(fill="both", expand=True, pady=(2, 10))

        def save() -> None:
            team_name = dialog.value("name")
            if not team_name:
                messagebox.showwarning("Missing data", "Enter a team name.")
                return

            team_id = self.dashboard.services["team"].create_team(class_id, team_name, None)
            for user_id in picker.selected_ids():
                self.dashboard.services["team"].add_team_member(team_id, user_id)

            dialog.destroy()
            self._refresh_teams()

        dialog.add_actions(save, confirm_text="Create")

    def _delete_team(self, team_id: int) -> None:
        if not messagebox.askyesno("Confirm", "Delete this team and its data?"):
            return
        self.dashboard.services["team"].delete_team(team_id)
        self.dashboard.slide_over.clear()
        self._refresh_teams()

    def _add_team_member(self, team_id: int) -> None:
        options, mapping = self._student_options()
        if not options:
            messagebox.showwarning("No students", "No students available to add.")
            return

        dialog = FormDialog(self, title="Add Member")
        dialog.add_select("student", label="Student", values=options)

        def save() -> None:
            selected = dialog.value("student")
            user_id = mapping.get(selected)
            if not user_id:
                messagebox.showwarning("No student", "Select a student to add.")
                return
            self.dashboard.services["team"].add_team_member(team_id, user_id)
            dialog.destroy()
            self._on_team_selected(team_id)

        dialog.add_actions(save, confirm_text="Add")

    def _send_invite(self, team_id: int) -> None:
        options, mapping = self._student_options()
        if not options:
            messagebox.showwarning("No students", "No students available to invite.")
            return

        dialog = FormDialog(self, title="Send Invite")
        dialog.add_select("student", label="Student", values=options)

        def save() -> None:
            selected = dialog.value("student")
            user_id = mapping.get(selected)
            if not user_id:
                messagebox.showwarning("No student", "Select a student to invite.")
                return
            self.services["team"].create_invitation(team_id, user_id)
            dialog.destroy()
            self._on_team_selected(team_id)

        dialog.add_actions(save, confirm_text="Send")

    def _set_principal(self, team_id: int) -> None:
        options, mapping = self._student_options()
        if not options:
            messagebox.showwarning("No students", "No students available.")
            return

        dialog = FormDialog(self, title="Set Principal")
        dialog.add_select("student", label="Principal", values=options)

        def save() -> None:
            selected = dialog.value("student")
            user_id = mapping.get(selected)
            if not user_id:
                messagebox.showwarning("No student", "Select a principal student.")
                return
            self.dashboard.services["team"].update_team_principal(team_id, user_id)
            dialog.destroy()
            self._refresh_teams()
            self._on_team_selected(team_id)

        dialog.add_actions(save, confirm_text="Set")
