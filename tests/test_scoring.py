import json
from riskscenariostest import (
    get_required_task_weights,
    compute_scenario_coverage,
    run_simulation,
    compute_portfolio_summary,
)


def test_get_required_task_weights():
    scenario = {
        "required_tasks": [
            {"task_id": "T1", "weight": 10},
            {"task_id": "T2", "weight": 5},
            {"weight": 3},  # missing task_id should be skipped
        ]
    }

    weights = get_required_task_weights(scenario)
    assert weights == {"T1": 10.0, "T2": 5.0}


def test_compute_scenario_coverage_and_portfolio():
    plan_data = {
        "role_task_coverage_reference": {
            "R1": {"tasks_used_in_simulation": ["T1", "T2"]}
        },
        "scenarios": [
            {
                "id": "S1",
                "name": "Test Scenario",
                "likelihood": 1,
                "impact": 1,
                "risk_score": 1,
                "required_tasks": [
                    {"task_id": "T1", "weight": 10},
                    {"task_id": "T2", "weight": 10},
                ],
                "coverage_evaluation": {
                    "covered_by_roles": [
                        {"entity_id": "R1", "covers_tasks": ["T1", "T2"]}
                    ],
                    "control_modifier": 1.0,
                    "execution_factor": 1.0,
                },
            }
        ],
    }

    sim = run_simulation(plan_data)
    summary = sim["portfolio_summary"]

    # With full coverage and modifiers 1.0 we expect ~100% risk reduction
    from pytest import approx
    assert summary["average_risk_reduction_percent"] == approx(100.0)
    assert summary["average_coverage_percent"] == approx(100.0)


def test_compute_scenario_with_partial_and_invalid_tasks():
    # scenario where some tasks are uncovered and some claimed tasks are invalid
    plan_data = {
        "role_task_coverage_reference": {
            "R1": {"tasks_used_in_simulation": ["T1"]},
            "R2": {"tasks_used_in_simulation": ["T3"]},
        },
        "scenarios": [
            {
                "id": "S2",
                "name": "Partial Scenario",
                "required_tasks": [
                    {"task_id": "T1", "weight": 5},
                    {"task_id": "T2", "weight": 5},
                ],
                "coverage_evaluation": {
                    "covered_by_roles": [
                        {"entity_id": "R1", "covers_tasks": ["T1", "T2"]},
                        {"entity_id": "R2", "covers_tasks": ["T2"]},
                    ],
                    "control_modifier": 1.0,
                    "execution_factor": 1.0,
                },
            }
        ],
    }

    sim = run_simulation(plan_data)
    results = sim["results"]
    assert len(results) == 1
    res = results[0]
    # T2 is not in any role reference so it should not count as covered
    assert res["covered_tasks_count"] == 1
    assert "T2" in res["uncovered_tasks"]
    # coverage percent should be approximately 50%
    from pytest import approx
    assert res["coverage_percent"] == approx(50.0)
