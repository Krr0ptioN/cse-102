from __future__ import annotations

import tkinter as tk

from app.ui.components.primitives import Button, Card, Input, Label, Select


class AuthCard:
    """Auth card for sign-in / sign-up."""

    def __init__(
        self,
        master,
        *,
        sign_up_mode: bool,
        on_submit,
        on_switch,
    ) -> None:
        self.frame = Card(master)

        self.title_text = "Create Account" if sign_up_mode else "Welcome Back"
        self.subtitle_text = (
            "Use this form to create your account"
            if sign_up_mode
            else "Sign in to continue"
        )
        self.action_text = "Create Account" if sign_up_mode else "Sign In"
        self.switch_prompt = (
            "Already have an account?" if sign_up_mode else "Need an account?"
        )
        self.switch_action = "Sign In" if sign_up_mode else "Sign Up"

        Label(self.frame, text=self.title_text, weight="bold").pack(pady=(22, 8), padx=28)
        Label(self.frame, text=self.subtitle_text, variant="muted").pack(
            pady=(0, 14), padx=28
        )

        form = Card(self.frame)
        form.pack(fill="x", padx=20, pady=(0, 12))
        Label(form, text=self.action_text, weight="bold").pack(
            anchor="w", padx=12, pady=(10, 6)
        )

        self.name_entry = None
        if sign_up_mode:
            self.name_entry = Input(form, placeholder="Full name")
            self.name_entry.pack(fill="x", padx=12, pady=4)

        self.email_entry = Input(form, placeholder="Email")
        self.email_entry.pack(fill="x", padx=12, pady=4)

        self.password_entry = Input(form, placeholder="Password", show="*")
        self.password_entry.pack(fill="x", padx=12, pady=4)

        self.role_var = tk.StringVar(value="student")
        self.role_select = None
        if sign_up_mode:
            self.role_select = Select(
                form,
                values=["student", "teacher"],
                variable=self.role_var,
            )
            self.role_select.pack(fill="x", padx=12, pady=4)

        Button(
            form,
            text=self.action_text,
            command=lambda: on_submit(self.__values(sign_up_mode)),
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

    def __values(self, sign_up_mode: bool) -> dict[str, str]:
        data = {
            "email": self.email_entry.get().strip(),
            "password": self.password_entry.get(),
        }
        if sign_up_mode:
            data["name"] = self.name_entry.get().strip() if self.name_entry else ""
            data["role"] = self.role_var.get().strip() or "student"
        return data

    def place_center(self) -> None:
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
