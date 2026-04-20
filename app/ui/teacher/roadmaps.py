from __future__ import annotations

import tkinter as tk

from libs.ui_kit import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    Label,
    SectionHeader,
    PhaseListView,
    palette
)


class RoadmapReviewSection(tk.Frame):
    def __init__(self, master, on_add_comment, on_approve, on_select) -> None:
        colors_bg = (
            master["bg"] if isinstance(master, tk.BaseWidget) else palette()["bg"]
        )
        super().__init__(master, bg=colors_bg)
        self.on_add_comment = on_add_comment
        self.on_approve = on_approve
        self.on_select = on_select
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Roadmap Review",
            subtitle="Review team implementation plans and provide feedback.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        # Horizontal split: Left list of roadmaps, Right detail tree
        main_body = tk.Frame(self, bg=self["bg"])
        main_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        main_body.columnconfigure(0, weight=1)
        main_body.columnconfigure(1, weight=2)
        main_body.rowconfigure(0, weight=1)

        # Left Column: Roadmap List
        list_card = Card(main_body)
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        
        Label(list_card, text="Submitted Plans", weight="bold").pack(anchor="w", padx=12, pady=12)
        
        self.roadmap_table = DataTable(
            list_card, ["Id", "Team", "Status"], height=10
        )
        self.roadmap_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.roadmap_table.bind("<<TreeviewSelect>>", lambda _e: self._on_roadmap_click())

        # Right Column: Phase Detail
        detail_card = Card(main_body)
        detail_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        
        Label(detail_card, text="Plan Detail", weight="bold").pack(anchor="w", padx=12, pady=12)
        
        self.phase_list = PhaseListView(detail_card)
        self.phase_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def set_roadmap_rows(self, rows: list[tuple]) -> None:
        # Filter for only relevant columns for the small table
        short_rows = [(r[0], r[1], r[3]) for r in rows]
        self.roadmap_table.set_rows(short_rows)

    def set_phase_data(self, phases: list[dict]) -> None:
        self.phase_list.set_phases(phases)

    def selected_roadmap_id(self) -> int | None:
        selection = self.roadmap_table.selection()
        if not selection:
            return None
        return int(self.roadmap_table.item(selection[0], "values")[0])

    def _on_roadmap_click(self) -> None:
        self.on_select() # This triggers the page logic to fetch phases and update slide-over
