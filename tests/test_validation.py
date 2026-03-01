import json
import pytest
from pydantic import ValidationError

from schemas import validate_plan


def test_validate_good_plan():
    with open("risk_scenarios.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Should not raise
    plan = validate_plan(data)
    assert plan.scenarios is not None


def test_validate_missing_required_fields():
    # a scenario record missing required fields should cause validation error
    bad = {"scenarios": [{}]}
    with pytest.raises(ValidationError):
        validate_plan(bad)
