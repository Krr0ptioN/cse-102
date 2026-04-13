from __future__ import annotations

import tkinter as tk

import numpy as np
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.libs.ui_kit.design_system.typography import Typography


sns.set_theme(style="whitegrid")


def build_gantt_figure(tasks: list[dict]) -> Figure:
    fig = Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)

    if not tasks:
        ax.set_title("Gantt (no tasks)")
        return fig

    y_positions = list(range(len(tasks)))
    starts = []
    lengths = []
    labels = []
    current = 0
    for task in tasks:
        weight = max(task.get("weight", 0), 1)
        starts.append(current)
        lengths.append(weight)
        labels.append(task.get("title", "Task"))
        current += weight

    colors = sns.color_palette("crest", len(tasks))
    ax.barh(y_positions, lengths, left=starts, color=colors)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Weight")
    ax.set_title("Gantt (weight-based)")
    fig.tight_layout()
    return fig


def build_burndown_figure(tasks: list[dict]) -> Figure:
    fig = Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)

    total = sum(task.get("weight", 0) for task in tasks)
    remaining = total
    points = [remaining]
    for task in tasks:
        if task.get("status") == "Done":
            remaining -= task.get("weight", 0)
        points.append(remaining)

    x = list(range(len(points)))
    sns.lineplot(x=x, y=points, marker="o", ax=ax, color="#2a9d8f")
    if len(points) > 1:
        ideal = np.linspace(total, 0, len(points))
        sns.lineplot(x=x, y=ideal, ax=ax, color="#8d99ae", linestyle="--")

    ax.set_title("Burndown")
    ax.set_xlabel("Task index")
    ax.set_ylabel("Remaining weight")
    fig.tight_layout()
    return fig


def build_progress_figure(checkins: list[dict]) -> Figure:
    fig = Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)

    if not checkins:
        ax.set_title("Progress (no check-ins)")
        return fig

    ordered = sorted(checkins, key=lambda row: row.get("week_start", ""))
    labels = [row.get("week_start", "") for row in ordered]
    percents = [row.get("percent", 0) for row in ordered]
    x = list(range(len(percents)))

    sns.lineplot(x=x, y=percents, marker="o", ax=ax, color="#457b9d")
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_title("Progress Over Time")
    ax.set_xlabel("Week start")
    ax.set_ylabel("Completion %")
    fig.tight_layout()
    return fig


def show_reports_window(
    parent: tk.Widget,
    title: str,
    team_name: str,
    tasks: list[dict],
    checkins: list[dict],
) -> None:
    window = tk.Toplevel(parent)
    window.title(title)

    header = tk.Frame(window)
    header.pack(fill="x", padx=12, pady=10)
    tk.Label(
        header,
        text=title,
        font=(Typography.primary_font_family(), 14, "bold"),
    ).pack(anchor="w")
    tk.Label(header, text=f"Team: {team_name}").pack(anchor="w")

    gantt_fig = build_gantt_figure(tasks)
    burn_fig = build_burndown_figure(tasks)
    progress_fig = build_progress_figure(checkins)

    for fig, label in [
        (gantt_fig, "Gantt"),
        (burn_fig, "Burndown"),
        (progress_fig, "Progress"),
    ]:
        frame = tk.LabelFrame(window, text=label)
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
