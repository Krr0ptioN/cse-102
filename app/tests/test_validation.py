from app.core.services.validation import validate_roadmap


def test_roadmap_requires_three_phases():
    result = validate_roadmap(phases=[{"tasks": [1]}])
    assert result["ok"] is False


def test_roadmap_requires_task_per_phase():
    result = validate_roadmap(phases=[{"tasks": [1]}, {"tasks": []}, {"tasks": [1]}])
    assert result["ok"] is False


def test_roadmap_weight_warning():
    result = validate_roadmap(phases=[{"tasks": [20]}, {"tasks": [20]}, {"tasks": [10]}])
    assert result["ok"] is True
    assert result["weight_warning"] is True
