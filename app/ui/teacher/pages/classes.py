from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from libs.ui_kit.design_system import palette
from libs.ui_kit import Button, Card, EmptyState, Input, SectionHeader
from ui.shared.page import Page


class TeacherClassesPage(Page):
    title = "Classes"
    route = "classes"

    def __init__(self, dashboard) -> None:
        super().__init__(dashboard)

    def on_mount(self) -> None:
        self.colors = palette()

        header = SectionHeader(
            self,
            title="Class Management",
            subtitle="Create classes and choose which class is active across teacher tools.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        create_card = Card(self)
        create_card.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(
            create_card,
            text="Create New Class",
            bg=self.colors.surface,
            fg=self.colors.text,
            font=("TkDefaultFont", 11, "bold"),
        ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))

        tk.Label(
            create_card,
            text="Class name",
            bg=self.colors.surface,
            fg=self.colors.text,
        ).grid(row=1, column=0, sticky="w")
        self.name_entry = Input(create_card, placeholder="e.g. CSE-102")
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(6, 12))

        tk.Label(
            create_card,
            text="Term",
            bg=self.colors.surface,
            fg=self.colors.text,
        ).grid(row=1, column=2, sticky="w")
        self.term_entry = Input(create_card, placeholder="e.g. Spring 2026")
        self.term_entry.grid(row=1, column=3, sticky="ew", padx=(6, 12))

        Button(
            create_card,
            text="Create Class",
            command=self._create_class,
            size="sm",
        ).grid(row=1, column=4, sticky="ew")

        create_card.columnconfigure(1, weight=3)
        create_card.columnconfigure(3, weight=2)
        create_card.columnconfigure(4, minsize=110)

        self.status_label = tk.Label(
            self,
            text="",
            bg=self["bg"],
            fg=self.colors.muted,
        )
        self.status_label.pack(anchor="w", padx=12, pady=(0, 6))

        container = tk.Frame(self, bg=self["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.cards_canvas = tk.Canvas(
            container,
            bg=self["bg"],
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.cards_canvas.yview,
        )
        self.cards_canvas.configure(yscrollcommand=scrollbar.set)

        self.cards_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cards_frame = tk.Frame(self.cards_canvas, bg=self["bg"])
        self._cards_window = self.cards_canvas.create_window(
            (0, 0),
            window=self.cards_frame,
            anchor="nw",
        )

        self.cards_frame.bind("<Configure>", self._on_cards_configure)
        self.cards_canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_cards_configure(self, _event) -> None:
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.cards_canvas.itemconfigure(self._cards_window, width=event.width)

    def _create_class(self) -> None:
        name = self.name_entry.get().strip()
        term = self.term_entry.get().strip()
        if not name or not term:
            messagebox.showwarning("Missing data", "Enter class name and term.")
            return

        class_id = self.dashboard.services["class"].create_class(
            name,
            term,
            owner_user_id=self.dashboard.current_user.id,
        )
        self.dashboard.set_active_class(class_id)
        self.name_entry.delete(0, tk.END)
        self.term_entry.delete(0, tk.END)
        self._refresh()

    def on_show(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        for child in list(self.cards_frame.winfo_children()):
            child.destroy()

        classes = self.dashboard.services["class"].list_classes(
            owner_user_id=self.dashboard.current_user.id
        )
        if not classes:
            EmptyState(
                self.cards_frame,
                title="No classes yet",
                description="Create your first class to get started.",
            ).pack(fill="x", pady=8)
            self.status_label.configure(text="No active class")
            return

        active_text = "No active class"
        current_class_id = self.dashboard.class_id
        for index, class_item in enumerate(classes):
            card = self._build_class_card(class_item)
            row = index // 2
            col = index % 2
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            self.cards_frame.columnconfigure(col, weight=1)

            if class_item["id"] == current_class_id:
                active_text = (
                    f"Active class: {class_item['name']} ({class_item['term']})"
                )

        self.status_label.configure(text=active_text)

    def _build_class_card(self, class_item: dict) -> tk.Frame:
        class_id = class_item["id"]
        stats = self._class_stats(class_id)
        is_active = class_id == self.dashboard.class_id

        card = tk.Frame(
            self.cards_frame,
            bg=self.colors.surface,
            highlightbackground=self.colors.primary
            if is_active
            else self.colors.border,
            highlightthickness=2 if is_active else 1,
            bd=0,
            padx=12,
            pady=10,
        )

        title_row = tk.Frame(card, bg=self.colors.surface)
        title_row.pack(fill="x")
        tk.Label(
            title_row,
            text=class_item["name"],
            bg=self.colors.surface,
            fg=self.colors.text,
            font=("TkDefaultFont", 11, "bold"),
        ).pack(side="left")
        if is_active:
            tk.Label(
                title_row,
                text="ACTIVE",
                bg=self.colors.primary,
                fg="#ffffff",
                padx=6,
                pady=1,
            ).pack(side="right")

        tk.Label(
            card,
            text=f"Term: {class_item['term']}",
            bg=self.colors.surface,
            fg=self.colors.muted,
        ).pack(anchor="w", pady=(4, 10))

        stats_grid = tk.Frame(card, bg=self.colors.surface)
        stats_grid.pack(fill="x")
        stats_pairs = [
            ("Students", stats["students"]),
            ("Teams", stats["teams"]),
            ("Roadmaps", stats["roadmaps"]),
            ("Check-ins", stats["checkins"]),
        ]
        for idx, (label, value) in enumerate(stats_pairs):
            box = tk.Frame(
                stats_grid,
                bg=self.colors.panel,
                highlightbackground=self.colors.border,
                highlightthickness=1,
                bd=0,
                padx=8,
                pady=6,
            )
            box.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=4, pady=4)
            tk.Label(
                box,
                text=str(value),
                bg=self.colors.panel,
                fg=self.colors.text,
                font=("TkDefaultFont", 11, "bold"),
            ).pack(anchor="w")
            tk.Label(
                box,
                text=label,
                bg=self.colors.panel,
                fg=self.colors.muted,
            ).pack(anchor="w")

        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        Button(
            card,
            text="Use This Class" if not is_active else "Currently Active",
            state="normal" if not is_active else "disabled",
            command=lambda cid=class_id: self._select_class(cid),
            size="sm",
        ).pack(fill="x", pady=(12, 0))

        return card

    def _class_stats(self, class_id: int) -> dict[str, int]:
        services = self.dashboard.services
        teams = services["team"].list_teams(class_id)
        roadmaps = services["roadmap"].list_roadmaps_for_class(class_id)
        checkins = services["checkin"].list_checkins_for_class(class_id)

        student_ids: set[int] = set()
        for team in teams:
            members = services["team"].list_team_members(team["id"])
            for member in members:
                student_ids.add(int(member["id"]))

        return {
            "students": len(student_ids),
            "teams": len(teams),
            "roadmaps": len(roadmaps),
            "checkins": len(checkins),
        }

    def _select_class(self, class_id: int) -> None:
        self.dashboard.set_active_class(class_id)
        self._refresh()
