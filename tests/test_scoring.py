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

    # With full coverage and modifiers 1.0 we expect 100% risk reduction
    assert summary["average_risk_reduction_percent"] == 100.0
    assert summary["average_coverage_percent"] == 100.0
