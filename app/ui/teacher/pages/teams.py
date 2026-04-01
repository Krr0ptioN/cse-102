from __future__ import annotations

import tkinter as tk

from app.ui.teacher import TeamSection
from app.ui.forms import TeamForm, StudentForm
from app.ui.components import Button, Modal, bind_modal_keys
from tkinter import messagebox


class TeacherTeamsPage(tk.Frame):
    title = "Teams"

    def __init__(self, master, services: dict, class_id: int | None) -> None:
        colors_bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=colors_bg)
        self.services = services
        self.class_id = class_id

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
        self.team_section.pack(fill="both", expand=True, padx=8, pady=8)

    # --- data refresh
    def _refresh_students(self) -> None:
        students = self.services["class"].list_users(role="student")
        choices = [f"{s['id']} {s['name']}" for s in students]
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
            self.team_section.set_member_rows([])
            self.team_section.set_invite_rows([])
            return
        members = self.services["team"].list_team_members(team_id)
        rows = [(m["id"], m["name"], m["email"], m["role"]) for m in members]
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

    # --- actions
    def _team_create_modal(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return
        modal = Modal(self, "Create Team")
        form = TeamForm()
        form.render(modal.body, columns=1)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            self.services["team"].create_team(self.class_id, data["name"], None)
            modal.destroy()
            self._refresh_teams()

        bind_modal_keys(modal, save)
        Button(
            modal.actions, text="Cancel", command=modal.destroy, variant="outline"
        ).pack(side="right", padx=4)
        Button(modal.actions, text="Create", command=save, size="sm").pack(
            side="right", padx=4
        )

    def _edit_team_modal(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        row = self.team_section.selected_team_row()
        if not row:
            return
        modal = Modal(self, "Edit Team")
        form = TeamForm()
        form.render(modal.body, columns=1)
        form.set_data({"name": row[1]})

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            self.services["team"].update_team(team_id, data["name"])
            modal.destroy()
            self._refresh_teams()

        bind_modal_keys(modal, save)
        Button(
            modal.actions, text="Cancel", command=modal.destroy, variant="outline"
        ).pack(side="right", padx=4)
        Button(modal.actions, text="Save", command=save, size="sm").pack(
            side="right", padx=4
        )

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
        selection = self.team_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No student", "Select a student to add.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.services["team"].add_team_member(team_id, user_id)
        self._refresh_team_members()

    def _send_invite(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.team_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No student", "Select a student to invite.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.services["team"].create_invitation(team_id, user_id)
        self._refresh_team_invitations()

    def _set_principal(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.team_section.selected_principal_label()
        if not selection:
            messagebox.showwarning("No student", "Select a principal student.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.services["team"].update_team_principal(team_id, user_id)
        self._refresh_teams()

    def _set_member_role(self) -> None:
        team_id = self.team_section.selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        user_id = self.team_section.selected_member_id()
        if not user_id:
            messagebox.showwarning("No member", "Select a team member.")
            return
        role = self.team_section.selected_role()
        if not role:
            messagebox.showwarning("No role", "Select a role.")
            return
        self.services["team"].set_member_role(team_id, user_id, role)
        self._refresh_team_members()
