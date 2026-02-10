from __future__ import annotations


def validate_roadmap(phases: list[dict]) -> dict:
    if len(phases) < 3:
        return {"ok": False, "reason": "Need at least 3 phases"}
    for phase in phases:
        if not phase.get("tasks"):
            return {"ok": False, "reason": "Each phase needs a task"}
    total = 0
    for phase in phases:
        total += sum(phase["tasks"])
    return {"ok": True, "weight_warning": total != 100}
