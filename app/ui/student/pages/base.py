from __future__ import annotations

import tkinter as tk
from libs.ui_kit import SectionHeader
from ui.shared.page import Page


class StudentSectionPage(Page):
    subtitle: str = ""

    def on_mount(self) -> None:
        SectionHeader(self, title=self.title, subtitle=self.subtitle).pack(
            fill="x", padx=12, pady=(12, 8)
        )
        self.body = tk.Frame(self, bg=self["bg"])
        self.body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
