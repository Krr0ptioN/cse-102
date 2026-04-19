from __future__ import annotations

import math
import os
import tkinter as tk

import numpy as np
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from libs.ui_kit import Button, Card, SectionHeader
from libs.ui_kit.design_system import palette as design_palette
from libs.ui_kit.design_system import Typography

try:  # Optional dependency; available when APP_UI=ctk and customtkinter is installed.
    import customtkinter as ctk
except Exception:  # pragma: no cover - fallback to Tk
    ctk = None  # type: ignore


DEFAULT_CHECKIN_PROJECTION = 4
MAX_CHECKIN_PROJECTION = 24


def _ui_palette():
    return design_palette()


def _configure_chart_theme() -> None:
    colors = _ui_palette()
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": colors.bg,
            "axes.facecolor": colors.surface,
            "axes.edgecolor": colors.border,
            "axes.labelcolor": colors.text,
            "axes.titlecolor": colors.text,
            "grid.color": colors.border,
            "xtick.color": colors.text,
            "ytick.color": colors.text,
            "font.family": Typography.primary_font_family(),
        },
    )


def _style_axis(ax) -> None:
    colors = _ui_palette()
    ax.grid(axis="y", color=colors.border, alpha=0.7, linewidth=0.8)
    ax.tick_params(colors=colors.text, labelsize=9)
    ax.xaxis.label.set_color(colors.text)
    ax.yaxis.label.set_color(colors.text)
    ax.title.set_color(colors.text)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(colors.border)
    ax.spines["bottom"].set_color(colors.border)


def _estimate_checkins_progress(checkins: list[dict]) -> tuple[int, int, int]:
    completed = len(checkins)
    if completed == 0:
        return 0, DEFAULT_CHECKIN_PROJECTION, 0

    ordered = sorted(checkins, key=lambda row: row.get("week_start", ""))
    latest_percent = int(ordered[-1].get("percent", 0) or 0)

    if latest_percent <= 0:
        projected_total = min(MAX_CHECKIN_PROJECTION, completed + DEFAULT_CHECKIN_PROJECTION)
    else:
        projected_total = int(math.ceil((completed * 100) / latest_percent))
        projected_total = max(completed, min(projected_total, MAX_CHECKIN_PROJECTION))

    remaining = max(projected_total - completed, 0)
    return completed, remaining, latest_percent


_configure_chart_theme()


def build_gantt_figure(tasks: list[dict]) -> Figure:
    colors = _ui_palette()
    fig = Figure(figsize=(6, 3), dpi=100)
    fig.patch.set_facecolor(colors.bg)
    ax = fig.add_subplot(111)

    if not tasks:
        ax.set_title("Gantt (no tasks)")
        _style_axis(ax)
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
    _style_axis(ax)
    fig.tight_layout()
    return fig


def build_burndown_figure(tasks: list[dict]) -> Figure:
    colors = _ui_palette()
    fig = Figure(figsize=(6, 3), dpi=100)
    fig.patch.set_facecolor(colors.bg)
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
    _style_axis(ax)
    fig.tight_layout()
    return fig


def build_progress_figure(checkins: list[dict]) -> Figure:
    colors = _ui_palette()
    fig = Figure(figsize=(6, 3), dpi=100)
    fig.patch.set_facecolor(colors.bg)
    ax = fig.add_subplot(111)

    if not checkins:
        ax.set_title("Progress (no check-ins)")
        _style_axis(ax)
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
    _style_axis(ax)
    fig.tight_layout()
    return fig


def build_checkins_left_figure(checkins: list[dict]) -> Figure:
    colors = _ui_palette()
    fig = Figure(figsize=(6, 3), dpi=100)
    fig.patch.set_facecolor(colors.bg)
    ax = fig.add_subplot(111)

    completed, remaining, latest_percent = _estimate_checkins_progress(checkins)
    sns.barplot(
        x=["Completed", "Left"],
        y=[completed, remaining],
        hue=["Completed", "Left"],
        ax=ax,
        palette={"Completed": colors.primary, "Left": colors.muted},
        legend=False,
        width=0.6,
    )

    max_value = max([completed, remaining, 1])
    ax.set_ylim(0, max_value * 1.3)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for index, value in enumerate([completed, remaining]):
        ax.text(
            index,
            value + (max_value * 0.05),
            str(value),
            ha="center",
            va="bottom",
            color=colors.text,
            fontsize=10,
            fontweight="bold",
        )

    ax.set_title("Estimated Check-ins Left")
    ax.set_xlabel("")
    ax.set_ylabel("Check-ins")
    ax.text(
        0.5,
        1.03,
        f"Latest roadmap completion: {latest_percent}%",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        color=colors.muted,
        fontsize=9,
    )
    _style_axis(ax)
    fig.tight_layout()
    return fig


def show_reports_window(
    parent: tk.Widget,
    title: str,
    team_name: str,
    tasks: list[dict],
    checkins: list[dict],
) -> None:
    colors = _ui_palette()
    use_ctk = ctk is not None and os.getenv("APP_UI", "ctk").lower() == "ctk"
    if use_ctk:
        window = ctk.CTkToplevel(parent)
        window.configure(fg_color=colors.bg)
    else:
        window = tk.Toplevel(parent)
        window.configure(bg=colors.bg)
    window.title(title)
    window.minsize(860, 700)

    if use_ctk:
        shell = ctk.CTkFrame(window, fg_color="transparent")
    else:
        shell = tk.Frame(window, bg=colors.bg)
    shell.pack(fill="both", expand=True, padx=12, pady=12)

    header_card = Card(shell)
    header_card.pack(fill="x", padx=4, pady=(0, 8))
    SectionHeader(
        header_card,
        title=title,
        subtitle=f"Team: {team_name}",
    ).pack(fill="x", padx=10, pady=(10, 8))

    if use_ctk:
        actions = ctk.CTkFrame(header_card, fg_color="transparent")
    else:
        actions = tk.Frame(header_card, bg=colors.panel)
    actions.pack(fill="x", padx=10, pady=(0, 10))
    Button(
        actions,
        text="Close",
        variant="outline",
        size="sm",
        command=window.destroy,
    ).pack(side="right")

    gantt_fig = build_gantt_figure(tasks)
    burn_fig = build_burndown_figure(tasks)
    progress_fig = build_progress_figure(checkins)
    checkins_left_fig = build_checkins_left_figure(checkins)

    for fig, label in [
        (gantt_fig, "Gantt"),
        (burn_fig, "Burndown"),
        (progress_fig, "Progress"),
        (checkins_left_fig, "Check-ins Left"),
    ]:
        chart_card = Card(shell)
        chart_card.pack(fill="both", expand=True, padx=4, pady=4)
        SectionHeader(chart_card, title=label).pack(fill="x", padx=10, pady=(10, 4))
        if use_ctk:
            chart_body = ctk.CTkFrame(chart_card, fg_color=colors.surface)
        else:
            chart_body = tk.Frame(chart_card, bg=colors.surface)
        chart_body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas = FigureCanvasTkAgg(fig, master=chart_body)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg=colors.surface, highlightthickness=0, bd=0)
        canvas_widget.pack(fill="both", expand=True)
