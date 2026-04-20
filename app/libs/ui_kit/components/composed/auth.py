from __future__ import annotations

import tkinter as tk

from ..primitives import Button, Card, Input, Label, Select


class AuthCard:
    """Base auth card. Subclasses define content and extra fields."""

    title_text = ""
    subtitle_text = ""
    action_text = ""
    switch_prompt = ""
    switch_action = ""
    include_name = False
    include_role = False

    def __init__(
        self,
        master,
        *,
        on_submit,
        on_switch,
    ) -> None:
        self.frame = Card(master, width=400, height=480)
        self._on_submit = on_submit

        self.name_entry = None
        self.role_var = tk.StringVar(value="student")
        self.role_select = None

        Label(self.frame, text=self.title_text, weight="bold").pack(
            pady=(22, 8), padx=28
        )
        Label(self.frame, text=self.subtitle_text, variant="muted").pack(
            pady=(0, 14), padx=28
        )

        form = Card(self.frame)
        form.pack(fill="x", padx=20, pady=(0, 12))
        Label(form, text=self.action_text, weight="bold").pack(
            anchor="w", padx=12, pady=(10, 6)
        )

        if self.include_name:
            self.name_entry = Input(form, placeholder="Full name")
            self.name_entry.pack(fill="x", padx=12, pady=4)

        self.email_entry = Input(form, placeholder="Email")
        self.email_entry.pack(fill="x", padx=12, pady=4)

        self.password_entry = Input(form, placeholder="Password", show="*")
        self.password_entry.pack(fill="x", padx=12, pady=4)

        if self.include_role:
            self.role_select = Select(
                form,
                values=["student", "teacher"],
                variable=self.role_var,
            )
            self.role_select.pack(fill="x", padx=12, pady=4)

        Button(
            form,
            text=self.action_text,
            command=self._submit,
            variant="default",
        ).pack(fill="x", padx=12, pady=(8, 12))

        Label(self.frame, text="Click below to switch forms", variant="muted").pack(
            pady=(0, 2)
        )
        Label(self.frame, text=self.switch_prompt, variant="muted").pack()

        switch_label = Label(
            self.frame, text=self.switch_action, variant="accent", weight="bold"
        )
        switch_label.pack(pady=(2, 18))
        switch_label.bind("<Button-1>", lambda _event: on_switch())

    def _submit(self) -> None:
        self._on_submit(self._values())

    def _values(self) -> dict[str, str]:
        data = {
            "email": self.email_entry.get().strip(),
            "password": self.password_entry.get(),
        }
        if self.include_name:
            data["name"] = self.name_entry.get().strip() if self.name_entry else ""
        if self.include_role:
            data["role"] = self.role_var.get().strip() or "student"
        return data

    def place_center(self) -> None:
        self.frame.place(relx=0.5, rely=0.5, anchor="center")


class SignInAuthCard(AuthCard):
    title_text = "Welcome Back"
    subtitle_text = "Sign in to continue"
    action_text = "Sign In"
    switch_prompt = "Need an account?"
    switch_action = "Sign Up"


class SignUpAuthCard(AuthCard):
    title_text = "Create Account"
    subtitle_text = "Use this form to create your account"
    action_text = "Create Account"
    switch_prompt = "Already have an account?"
    switch_action = "Sign In"
    include_name = True
    include_role = True
