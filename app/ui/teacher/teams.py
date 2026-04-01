from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.components import ButtonBar, DataTable, Section


class TeamSection(Section):
    def __init__(
        self,
        master,
        on_create,
        on_add_member,
        on_send_invite,
        on_set_principal,
        on_set_role,
        on_edit_team,
        on_delete_team,
        on_team_select,
    ) -> None:
        super().__init__(master, "Teams")
        self.on_create = on_create
        self.on_add_member = on_add_member
        self.on_send_invite = on_send_invite
        self.on_set_principal = on_set_principal
        self.on_set_role = on_set_role
        self.on_edit_team = on_edit_team
        self.on_delete_team = on_delete_team
        self.on_team_select = on_team_select
        self._build()

    def _build(self) -> None:
        tables = tk.Frame(self.body)
        tables.pack(fill="both", expand=True)
        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)

        self.team_table = DataTable(tables, ["Id", "Team", "Principal"], height=6)
        self.team_table.grid(row=0, column=0, sticky="nsew", padx=4, pady=6)
        self.team_table.bind("<<TreeviewSelect>>", lambda _e: self.on_team_select())

        self.member_table = DataTable(
            tables, ["Id", "Member", "Email", "Role"], height=6
        )
        self.member_table.grid(row=0, column=1, sticky="nsew", padx=4, pady=6)

        actions = ButtonBar(self.body)
        actions.pack(fill="x", pady=6)

        actions.add("Create Team", self.on_create)

        self.member_select = ttk.Combobox(actions, state="readonly")
        self.member_select.pack(side="left", padx=4)
        actions.add("Add Member", self.on_add_member)
        actions.add("Send Invite", self.on_send_invite)

        self.principal_select = ttk.Combobox(actions, state="readonly")
        self.principal_select.pack(side="left", padx=4)
        actions.add("Set Principal", self.on_set_principal)

        self.role_select = ttk.Combobox(actions, state="readonly")
        self.role_select["values"] = ["Member", "Lead", "Reviewer"]
        self.role_select.pack(side="left", padx=4)
        actions.add("Set Role", self.on_set_role)

        actions.add("Edit Team", self.on_edit_team)
        actions.add("Delete Team", self.on_delete_team)

        invite_block = tk.Frame(self.body)
        invite_block.pack(fill="both", expand=True, pady=6)
        tk.Label(invite_block, text="Invitations").pack(anchor="w")
        self.invite_table = DataTable(
            invite_block, ["Id", "Student", "Status"], height=4
        )
        self.invite_table.pack(fill="both", expand=True, pady=4)

    def set_team_rows(self, rows: list[tuple]) -> None:
        self.team_table.set_rows(rows)

    def set_member_rows(self, rows: list[tuple]) -> None:
        self.member_table.set_rows(rows)

    def set_invite_rows(self, rows: list[tuple]) -> None:
        self.invite_table.set_rows(rows)

    def set_student_choices(self, choices: list[str]) -> None:
        self.member_select["values"] = choices
        self.principal_select["values"] = choices

    def selected_team_id(self) -> int | None:
        selection = self.team_table.selection()
        if not selection:
            return None
        raw = self.team_table.item(selection[0], "values")[0]
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def selected_team_row(self) -> tuple | None:
        selection = self.team_table.selection()
        if not selection:
            return None
        row = self.team_table.item(selection[0], "values")
        if not row:
            return None
        try:
            int(row[0])
        except (TypeError, ValueError):
            return None
        return row

    def selected_member_id(self) -> int | None:
        selection = self.member_table.selection()
        if not selection:
            return None
        return int(self.member_table.item(selection[0], "values")[0])

    def selected_member_label(self) -> str:
        return self.member_select.get()

    def selected_principal_label(self) -> str:
        return self.principal_select.get()

    def selected_role(self) -> str:
        return self.role_select.get()
