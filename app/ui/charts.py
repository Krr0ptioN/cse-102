from __future__ import annotations

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def build_gantt_figure(tasks: list[dict]) -> Figure:
    fig = Figure(figsize=(5, 3), dpi=100)
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

    ax.barh(y_positions, lengths, left=starts)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Weight")
    ax.set_title("Gantt (weight-based)")
    fig.tight_layout()
    return fig


def build_burndown_figure(tasks: list[dict]) -> Figure:
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)

    total = sum(task.get("weight", 0) for task in tasks)
    remaining = total
    points = [remaining]
    for task in tasks:
        if task.get("status") == "Done":
            remaining -= task.get("weight", 0)
        points.append(remaining)

    ax.plot(range(len(points)), points, marker="o")
    ax.set_title("Burndown")
    ax.set_xlabel("Task index")
    ax.set_ylabel("Remaining weight")
    fig.tight_layout()
    return fig


def show_charts_window(parent: tk.Widget, title: str, tasks: list[dict]) -> None:
    window = tk.Toplevel(parent)
    window.title(title)

    gantt_fig = build_gantt_figure(tasks)
    burn_fig = build_burndown_figure(tasks)

    for fig, label in [(gantt_fig, "Gantt"), (burn_fig, "Burndown")]:
        frame = tk.LabelFrame(window, text=label)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
