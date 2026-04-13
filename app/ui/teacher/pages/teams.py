from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.libs.ui_kit.components import FormDialog, ToggleSelectionList
from app.ui.teacher import TeamSection


class TeacherTeamsPage(tk.Frame):
    title = "Teams"

    def __init__(self, master, services: dict, class_id: int | None) -> None:
        colors_bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=colors_bg)
        self.services = services
        self.class_id = class_id
        self._students: list[dict] = []
        self._member_rows: list[tuple] = []

        self._build()
        self._refresh_students()
        self._refresh_teams()

    def _build(self) -> None:
        self.team_section = TeamSection(
            self,
            self._team_create_modal,
            self._add_team_member,
            self._send_invite,
            self._set_principal,
            self._set_member_role,
            self._edit_team_modal,
            self._delete_team,
            self._refresh_team_members,
        )
        self.team_section.pack(fill="both", expand=True)

    # --- data refresh
    def _refresh_students(self) -> None:
        self._students = self.services["class"].list_users(role="student")
        choices = [f"{s['id']} {s['name']}" for s in self._students]
        self.team_section.set_student_choices(choices)

    def _refresh_teams(self) -> None:
        if not self.class_id:
            self.team_section.set_team_rows([])
            return
        teams = self.services["team"].list_teams(self.class_id)
        rows = []
        for team in teams:
            principal = team["principal_name"] or "-"
            rows.append((team["id"], team["name"], principal))
        self.team_section.set_team_rows(rows)
        if rows:
            first = self.team_section.team_table.get_children()[0]
            self.team_section.team_table.selection_set(first)
            self._refresh_team_members()

    def _refresh_team_members(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            self._member_rows = []
            self.team_section.set_member_rows([])
            self.team_section.set_invite_rows([])
            return
        members = self.services["team"].list_team_members(team_id)
        rows = [(m["id"], m["name"], m["email"], m["role"]) for m in members]
        self._member_rows = rows
        self.team_section.set_member_rows(rows)
        self._refresh_team_invitations()

    def _refresh_team_invitations(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            self.team_section.set_invite_rows([])
            return
        invites = self.services["team"].list_invitations_for_team(team_id)
        rows = [(i["id"], i["user"], i["status"]) for i in invites]
        self.team_section.set_invite_rows(rows)

    # --- dialog option builders
    def _student_options(self) -> tuple[list[str], dict[str, int]]:
        options: list[str] = []
        mapping: dict[str, int] = {}
        for student in self._students:
            label = f"{student['name']} ({student['email']})"
            options.append(label)
            mapping[label] = int(student["id"])
        return options, mapping

    def _member_options(self) -> tuple[list[str], dict[str, int]]:
        options: list[str] = []
        mapping: dict[str, int] = {}
        for user_id, name, email, role in self._member_rows:
            label = f"{name} ({email}) · {role}"
            options.append(label)
            mapping[label] = int(user_id)
        return options, mapping

    # --- actions
    def _team_create_modal(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return

        dialog = FormDialog(
            self,
            title="Create Team",
            subtitle="Create a team and optionally pre-add students.",
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

            team_id = self.services["team"].create_team(self.class_id, team_name, None)
            for user_id in picker.selected_ids():
                self.services["team"].add_team_member(team_id, user_id)

            dialog.destroy()
            self._refresh_teams()

        dialog.add_actions(save, confirm_text="Create")

    def _edit_team_modal(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        row = self.team_section.selected_team_row()
        if not row:
            return

        dialog = FormDialog(self, title="Edit Team")
        name_var = dialog.add_text("name", label="Team Name")
        name_var.set(row[1])

        def save() -> None:
            team_name = dialog.value("name")
            if not team_name:
                messagebox.showwarning("Missing data", "Enter a team name.")
                return
            self.services["team"].update_team(team_id, team_name)
            dialog.destroy()
            self._refresh_teams()

        dialog.add_actions(save, confirm_text="Save")

    def _delete_team(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this team and its data?"):
            return
        self.services["team"].delete_team(team_id)
        self._refresh_teams()

    def _add_team_member(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

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
            self.services["team"].add_team_member(team_id, user_id)
            dialog.destroy()
            self._refresh_team_members()

        dialog.add_actions(save, confirm_text="Add")

    def _send_invite(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

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
            self._refresh_team_invitations()

        dialog.add_actions(save, confirm_text="Send")

    def _set_principal(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

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
            self.services["team"].update_team_principal(team_id, user_id)
            dialog.destroy()
            self._refresh_teams()

        dialog.add_actions(save, confirm_text="Set")

    def _set_member_role(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

        options, mapping = self._member_options()
        if not options:
            messagebox.showwarning("No members", "No team members available.")
            return

        dialog = FormDialog(self, title="Set Member Role")
        dialog.add_select("member", label="Member", values=options)
        dialog.add_select(
            "role",
            label="Role",
            values=["Member", "Lead", "Reviewer"],
        )

        def save() -> None:
            selected_member = dialog.value("member")
            selected_role = dialog.value("role")
            user_id = mapping.get(selected_member)
            if not user_id:
                messagebox.showwarning("No member", "Select a team member.")
                return
            if not selected_role:
                messagebox.showwarning("No role", "Select a role.")
                return

            self.services["team"].set_member_role(team_id, user_id, selected_role)
            dialog.destroy()
            self._refresh_team_members()

        dialog.add_actions(save, confirm_text="Apply")
