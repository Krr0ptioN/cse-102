from __future__ import annotations

import tkinter as tk
from app.ui.components import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    Label,
    SectionHeader,
)
from app.ui.theme import palette


class TeamSection(tk.Frame):
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
        colors_bg = (
            master["bg"] if isinstance(master, tk.BaseWidget) else palette()["bg"]
        )
        super().__init__(master, bg=colors_bg)
        self.on_create = on_create
        self.on_add_member = on_add_member
        self.on_send_invite = on_send_invite
        self.on_set_principal = on_set_principal
        self.on_set_role = on_set_role
        self.on_edit_team = on_edit_team
        self.on_delete_team = on_delete_team
        self.on_team_select = on_team_select
        self._student_choices: list[str] = []
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Team Management",
            subtitle="Organize teams, assign principals, and manage invitations.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        tables = tk.Frame(self, bg=self["bg"])
        tables.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)

        team_card = Card(tables)
        team_card.grid(row=0, column=0, sticky="nsew", padx=6, pady=0)
        Label(team_card, text="Teams", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.team_filter_var = tk.StringVar(value="")
        team_filter_row = tk.Frame(team_card, bg=team_card["bg"])
        team_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(team_filter_row, text="Filter", bg=team_card["bg"]).pack(side="left")
        self.team_filter_entry = Input(
            team_filter_row,
            width=28,
            textvariable=self.team_filter_var,
        )
        self.team_filter_entry.pack(side="left", padx=(8, 8))
        self.team_filter_entry.bind(
            "<KeyRelease>", lambda _e: self._apply_team_filter()
        )
        Button(
            team_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_team_filter,
        ).pack(side="left")

        self.team_table = DataTable(team_card, ["Id", "Team", "Principal"], height=6)
        self.team_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.team_table.bind("<<TreeviewSelect>>", lambda _e: self.on_team_select())

        member_card = Card(tables)
        member_card.grid(row=0, column=1, sticky="nsew", padx=6, pady=0)
        Label(member_card, text="Members", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.member_filter_var = tk.StringVar(value="")
        member_filter_row = tk.Frame(member_card, bg=member_card["bg"])
        member_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(member_filter_row, text="Filter", bg=member_card["bg"]).pack(
            side="left"
        )
        self.member_filter_entry = Input(
            member_filter_row,
            width=28,
            textvariable=self.member_filter_var,
        )
        self.member_filter_entry.pack(side="left", padx=(8, 8))
        self.member_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_member_filter(),
        )
        Button(
            member_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_member_filter,
        ).pack(side="left")

        self.member_table = DataTable(
            member_card, ["Id", "Member", "Email", "Role"], height=6
        )
        self.member_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        actions_card = Card(self)
        actions_card.pack(fill="x", padx=12, pady=(0, 8))
        Label(actions_card, text="Actions", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 4)
        )

        actions = ButtonBar(actions_card)
        actions.pack(fill="x", padx=12, pady=(4, 12))

        actions.add("Create Team", self.on_create)
        actions.add("Add Member", self.on_add_member)
        actions.add("Send Invite", self.on_send_invite)
        actions.add("Set Principal", self.on_set_principal)
        actions.add("Set Role", self.on_set_role)
        actions.add("Edit Team", self.on_edit_team)
        actions.add("Delete Team", self.on_delete_team)

        self.action_hint = Label(
            actions_card,
            text="Actions open dialogs with guided selections.",
            variant="muted",
        )
        self.action_hint.pack(anchor="w", padx=12, pady=(0, 12))

        invite_card = Card(self)
        invite_card.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        Label(invite_card, text="Invitations", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        self.invite_filter_var = tk.StringVar(value="")
        invite_filter_row = tk.Frame(invite_card, bg=invite_card["bg"])
        invite_filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(invite_filter_row, text="Filter", bg=invite_card["bg"]).pack(
            side="left"
        )
        self.invite_filter_entry = Input(
            invite_filter_row,
            width=28,
            textvariable=self.invite_filter_var,
        )
        self.invite_filter_entry.pack(side="left", padx=(8, 8))
        self.invite_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_invite_filter(),
        )
        Button(
            invite_filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_invite_filter,
        ).pack(side="left")

        self.invite_table = DataTable(
            invite_card, ["Id", "Student", "Status"], height=4
        )
        self.invite_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def set_team_rows(self, rows: list[tuple]) -> None:
        self.team_table.set_rows(rows)
        self._apply_team_filter()

    def set_member_rows(self, rows: list[tuple]) -> None:
        self.member_table.set_rows(rows)
        self._apply_member_filter()

    def set_invite_rows(self, rows: list[tuple]) -> None:
        self.invite_table.set_rows(rows)
        self._apply_invite_filter()

    def set_student_choices(self, choices: list[str]) -> None:
        self._student_choices = list(choices)
        total = len(self._student_choices)
        suffix = "student" if total == 1 else "students"
        self.action_hint.configure(
            text=f"Actions open dialogs with guided selections ({total} {suffix} available)."
        )

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

    def _apply_team_filter(self) -> None:
        self.team_table.apply_filter(self.team_filter_var.get().strip(), columns=(1, 2))

    def _clear_team_filter(self) -> None:
        self.team_filter_var.set("")
        self._apply_team_filter()

    def _apply_member_filter(self) -> None:
        self.member_table.apply_filter(
            self.member_filter_var.get().strip(),
            columns=(1, 2, 3),
        )

    def _clear_member_filter(self) -> None:
        self.member_filter_var.set("")
        self._apply_member_filter()

    def _apply_invite_filter(self) -> None:
        self.invite_table.apply_filter(
            self.invite_filter_var.get().strip(), columns=(1, 2)
        )

    def _clear_invite_filter(self) -> None:
        self.invite_filter_var.set("")
        self._apply_invite_filter()
