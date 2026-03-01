import argparse
import json
from typing import Dict, List, Set, Any


def safe_round(value: float, digits: int = 1) -> float:
    return round(value + 1e-9, digits)


def build_entity_task_map(plan_data: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    Build a lookup: entity_id -> set(task_ids)
    """
    ref = plan_data.get("role_task_coverage_reference", {})
    entity_task_map: Dict[str, Set[str]] = {}

    for entity_id, entity_info in ref.items():
        entity_task_map[entity_id] = set(entity_info.get("tasks_used_in_simulation", []))

    return entity_task_map


def get_required_task_weights(scenario: Dict[str, Any]) -> Dict[str, float]:
    """
    Build a lookup: task_id -> weight for one scenario.
    """
    weights: Dict[str, float] = {}

    for item in scenario.get("required_tasks", []):
        task_id = item.get("task_id")
        if not task_id:
            continue
        weights[task_id] = float(item.get("weight", 0))

    return weights


def compute_scenario_coverage(
    scenario: Dict[str, Any],
    entity_task_map: Dict[str, Set[str]]
) -> Dict[str, Any]:
    """
    Recompute valid task coverage for one scenario.
    Only counts tasks that:
      1) are required by the scenario
      2) are claimed in covered_by_roles
      3) are actually allowed for that role/service in role_task_coverage_reference
    """
    required_weights = get_required_task_weights(scenario)
    required_task_ids = set(required_weights.keys())

    coverage_eval = scenario.get("coverage_evaluation", {})
    covered_by_roles = coverage_eval.get("covered_by_roles", [])

    covered_tasks: Set[str] = set()
    detailed_coverage: List[Dict[str, Any]] = []

    for entry in covered_by_roles:
        entity_id = entry.get("entity_id")
        claimed_tasks = set(entry.get("covers_tasks", []))
        reference_tasks = entity_task_map.get(entity_id, set())

        valid_tasks = claimed_tasks & reference_tasks & required_task_ids
        invalid_tasks = claimed_tasks - valid_tasks

        covered_tasks.update(valid_tasks)

        detailed_coverage.append({
            "entity_id": entity_id,
            "valid_tasks_count": len(valid_tasks),
            "valid_tasks": sorted(valid_tasks),
            "invalid_or_unmapped_tasks": sorted(invalid_tasks)
        })

    total_required_weight = sum(required_weights.values())
    covered_weight = sum(required_weights[t] for t in covered_tasks)
    uncovered_tasks = sorted(required_task_ids - covered_tasks)

    coverage_percent = 0.0
    if total_required_weight > 0:
        coverage_percent = (covered_weight / total_required_weight) * 100

    control_modifier = float(coverage_eval.get("control_modifier", 1.0))
    execution_factor = float(coverage_eval.get("execution_factor", 1.0))
    risk_reduction_percent = min(100.0, coverage_percent * control_modifier * execution_factor)

    return {
        "scenario_id": scenario.get("id"),
        "scenario_name": scenario.get("name"),
        "likelihood": scenario.get("likelihood"),
        "impact": scenario.get("impact"),
        "risk_score": scenario.get("risk_score"),
        "total_required_tasks": len(required_task_ids),
        "covered_tasks_count": len(covered_tasks),
        "total_required_weight": safe_round(total_required_weight, 2),
        "covered_weight": safe_round(covered_weight, 2),
        "coverage_percent": safe_round(coverage_percent, 1),
        "control_modifier": control_modifier,
        "execution_factor": execution_factor,
        "risk_reduction_percent": safe_round(risk_reduction_percent, 1),
        "covered_tasks": sorted(covered_tasks),
        "uncovered_tasks": uncovered_tasks,
        "detailed_coverage": detailed_coverage
    }


def build_executive_sentence(result: Dict[str, Any]) -> str:
    """
    Build the one-line executive statement for a scenario.
    """
    return (
        f'By executing the proposed hiring and upskilling plan, the organization mitigates '
        f'{result["risk_reduction_percent"]}% of the "{result["scenario_name"]}" scenario '
        f'by covering {result["covered_tasks_count"]} of {result["total_required_tasks"]} '
        f'critical NICE tasks ({result["covered_weight"]} of {result["total_required_weight"]} weighted points).'
    )


def score_all_scenarios(plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Score every scenario in the file.
    """
    entity_task_map = build_entity_task_map(plan_data)
    results: List[Dict[str, Any]] = []

    for scenario in plan_data.get("scenarios", []):
        result = compute_scenario_coverage(scenario, entity_task_map)
        result["executive_sentence"] = build_executive_sentence(result)
        results.append(result)

    return results


def rank_scenarios(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank scenarios from strongest mitigation to weakest.
    """
    return sorted(
        results,
        key=lambda x: (
            x["risk_reduction_percent"],
            x["coverage_percent"],
            x["covered_weight"]
        ),
        reverse=True
    )


def compute_portfolio_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute:
    - best mitigated scenario
    - weakest scenario
    - average portfolio risk reduction
    - average coverage
    """
    if not results:
        return {
            "best_mitigated": None,
            "weakest": None,
            "average_risk_reduction_percent": 0.0,
            "average_coverage_percent": 0.0,
            "scenario_count": 0
        }

    ranked = rank_scenarios(results)
    best = ranked[0]
    weakest = ranked[-1]

    avg_rr = sum(r["risk_reduction_percent"] for r in results) / len(results)
    avg_cov = sum(r["coverage_percent"] for r in results) / len(results)

    return {
        "best_mitigated": {
            "scenario_id": best["scenario_id"],
            "scenario_name": best["scenario_name"],
            "risk_reduction_percent": safe_round(best["risk_reduction_percent"], 1)
        },
        "weakest": {
            "scenario_id": weakest["scenario_id"],
            "scenario_name": weakest["scenario_name"],
            "risk_reduction_percent": safe_round(weakest["risk_reduction_percent"], 1)
        },
        "average_risk_reduction_percent": safe_round(avg_rr, 1),
        "average_coverage_percent": safe_round(avg_cov, 1),
        "scenario_count": len(results)
    }


def print_score_report(results: List[Dict[str, Any]]) -> None:
    """
    Detailed per-scenario report.
    """
    for result in results:
        print("=" * 90)
        print(f'Scenario: {result["scenario_name"]} ({result["scenario_id"]})')
        print(f'Likelihood: {result["likelihood"]} | Impact: {result["impact"]} | Risk Score: {result["risk_score"]}')
        print(f'Task coverage: {result["covered_tasks_count"]}/{result["total_required_tasks"]}')
        print(f'Weighted coverage: {result["covered_weight"]}/{result["total_required_weight"]}')
        print(f'Coverage %: {result["coverage_percent"]}%')
        print(f'Risk reduction %: {result["risk_reduction_percent"]}%')
        print(f'Uncovered tasks: {result["uncovered_tasks"] if result["uncovered_tasks"] else "None"}')
        print(result["executive_sentence"])
        print()


def print_ranking_table(ranked_results: List[Dict[str, Any]]) -> None:
    """
    Console ranking table for presentation/demo.
    """
    print("\n" + "=" * 90)
    print("SCENARIO RANKING TABLE")
    print("=" * 90)
    header = f'{"Rank":<6}{"Scenario ID":<12}{"Scenario Name":<38}{"Coverage %":<12}{"Risk Red. %":<14}'
    print(header)
    print("-" * 90)

    for idx, result in enumerate(ranked_results, start=1):
        row = (
            f'{idx:<6}'
            f'{result["scenario_id"]:<12}'
            f'{result["scenario_name"][:36]:<38}'
            f'{str(result["coverage_percent"]) + "%":<12}'
            f'{str(result["risk_reduction_percent"]) + "%":<14}'
        )
        print(row)

    print()


def print_portfolio_summary(summary: Dict[str, Any]) -> None:
    """
    Executive portfolio summary.
    """
    print("=" * 90)
    print("PORTFOLIO SUMMARY")
    print("=" * 90)

    if summary["scenario_count"] == 0:
        print("No scenarios found.")
        return

    best = summary["best_mitigated"]
    weakest = summary["weakest"]

    print(
        f'Best mitigated scenario: {best["scenario_name"]} ({best["scenario_id"]}) '
        f'with {best["risk_reduction_percent"]}% estimated risk reduction.'
    )
    print(
        f'Weakest scenario: {weakest["scenario_name"]} ({weakest["scenario_id"]}) '
        f'with {weakest["risk_reduction_percent"]}% estimated risk reduction.'
    )
    print(f'Average portfolio coverage: {summary["average_coverage_percent"]}%')
    print(f'Average portfolio risk reduction: {summary["average_risk_reduction_percent"]}%')
    print(f'Total scenarios analyzed: {summary["scenario_count"]}')
    print()


def print_presentation_talking_points(summary: Dict[str, Any]) -> None:
    """
    A clean block you can literally read in class/presentation.
    """
    if summary["scenario_count"] == 0:
        return

    best = summary["best_mitigated"]
    weakest = summary["weakest"]

    print("=" * 90)
    print("PRESENTATION TALKING POINTS")
    print("=" * 90)
    print(
        f'The proposed workforce plan delivers an average estimated risk reduction of '
        f'{summary["average_risk_reduction_percent"]}% across {summary["scenario_count"]} modeled scenarios.'
    )
    print(
        f'The strongest coverage is achieved in "{best["scenario_name"]}" with '
        f'{best["risk_reduction_percent"]}% estimated reduction.'
    )
    print(
        f'The most fragile scenario remains "{weakest["scenario_name"]}" with '
        f'{weakest["risk_reduction_percent"]}% estimated reduction, indicating where future investment should be prioritized.'
    )
    print()


def run_simulation(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full pipeline:
    - score all scenarios
    - rank them
    - compute portfolio summary
    """
    results = score_all_scenarios(plan_data)
    ranked = rank_scenarios(results)
    summary = compute_portfolio_summary(results)

    return {
        "results": results,
        "ranked_results": ranked,
        "portfolio_summary": summary
    }


# -----------------------------------------------------------------------------
# Example usage
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    def main() -> None:
        parser = argparse.ArgumentParser(description="Run risk scenario simulation")
        parser.add_argument("-i", "--input", default="risk_scenarios.json",
                            help="Path to the risk scenarios JSON file")
        parser.add_argument("-o", "--output", help="Optional output JSON file to save results")
        parser.add_argument("-q", "--quiet", action="store_true", help="Suppress console output")

        args = parser.parse_args()

        with open(args.input, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        simulation = run_simulation(plan_data)

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as outf:
                    json.dump(simulation, outf, indent=2)
            except Exception as e:
                print(f"Warning: could not write output file: {e}")

        if not args.quiet:
            results = simulation["results"]
            ranked_results = simulation["ranked_results"]
            summary = simulation["portfolio_summary"]

            print_score_report(results)
            print_ranking_table(ranked_results)
            print_portfolio_summary(summary)
            print_presentation_talking_points(summary)

    main()