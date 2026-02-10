from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.theme import palette


class AppShell(tk.Frame):
    def __init__(self, master, title: str, on_back) -> None:
        colors = palette()
        super().__init__(master, bg=colors["bg"])
        self.on_back = on_back
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, on_back)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.main = tk.Frame(self, bg=colors["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.main, title)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content = tk.Frame(self.main, bg=colors["bg"])
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)


class Sidebar(tk.Frame):
    def __init__(self, master, on_back) -> None:
        colors = palette()
        super().__init__(master, width=220, bg=colors["sidebar"])
        self.pack_propagate(False)

        tk.Label(
            self,
            text="Lifecycle",
            font=("Segoe UI", 16, "bold"),
            bg=colors["sidebar"],
            fg=colors["text"],
        ).pack(anchor="w", padx=16, pady=(16, 6))
        tk.Label(
            self,
            text="Project Manager",
            font=("Segoe UI", 9),
            bg=colors["sidebar"],
            fg=colors["muted"],
        ).pack(anchor="w", padx=16, pady=(0, 16))

        self.nav = tk.Frame(self, bg=colors["sidebar"])
        self.nav.pack(fill="x", padx=10)

        for label in ("Dashboard", "Roadmaps", "Teams", "Reports"):
            btn = tk.Button(self.nav, text=label, anchor="w", bg=colors["panel"])
            btn.pack(fill="x", pady=4)

        tk.Button(self, text="Back", command=on_back).pack(
            side="bottom", fill="x", padx=10, pady=12
        )


class Topbar(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        tk.Label(
            self, text=title, font=("Georgia", 18, "bold"), bg=colors["panel"]
        ).pack(side="left", padx=12, pady=12)
        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(side="right", padx=12)


class Section(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
        )
        header = tk.Frame(self, bg=colors["panel"])
        header.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(
            header, text=title, font=("Segoe UI", 11, "bold"), bg=colors["panel"]
        ).pack(side="left")
        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=12, pady=(0, 12))


class DataTable(ttk.Treeview):
    def __init__(self, master, columns: list[str], height: int = 6) -> None:
        super().__init__(master, columns=columns, show="headings", height=height)
        for col in columns:
            self.heading(col, text=col)
            self.column(col, anchor="w", width=120, stretch=True)

    def set_rows(self, rows: list[tuple]) -> None:
        for item in self.get_children():
            self.delete(item)
        for row in rows:
            self.insert("", "end", values=row)


class StatCard(tk.Frame):
    def __init__(self, master, label: str, value: str) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
        )
        self.label = tk.Label(
            self,
            text=label,
            font=("Segoe UI", 9),
            bg=colors["panel"],
            fg=colors["muted"],
        )
        self.label.pack(anchor="w", padx=8, pady=(6, 0))
        self.value = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 14, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        )
        self.value.pack(anchor="w", padx=8, pady=(0, 6))

    def set_value(self, value: str) -> None:
        self.value.config(text=value)


class DetailsDrawer(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            width=260,
        )
        self.pack_propagate(False)
        tk.Label(
            self,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        ).pack(anchor="w", padx=12, pady=(12, 6))
        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=12, pady=6)
        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(fill="x", padx=12, pady=(0, 12))

    def clear(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
        for child in self.actions.winfo_children():
            child.destroy()


class Modal(tk.Toplevel):
    def __init__(self, master, title: str) -> None:
        super().__init__(master)
        colors = palette()
        self.title(title)
        self.configure(bg=colors["panel"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.header = tk.Label(
            self,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        )
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=16, pady=8)

        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(fill="x", padx=16, pady=(0, 16))
