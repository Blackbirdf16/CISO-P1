# CISO-P1

Practical project: a small decision-support simulation that scores cybersecurity risk scenarios
against a proposed hiring/upskilling plan using NICE-task coverage and weighted risk-reduction
metrics.

Contents
- risk_scenarios.json — scenario, plan and reference data used by the scripts
- riskscenariostest.py — main scoring pipeline and presentation helpers
- roles_costs.csv — role catalogue and cost data used for planning/analysis
- NICE_all_roles_TK_report.pdf, 1_PracticaCISO (2).pdf — reference documents

Quick start (Windows)
1. Create and activate a virtual environment

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # PowerShell

2. Install dependencies (none required by current code). If you add packages,
   create `requirements.txt` and run:

   pip install -r requirements.txt

3. Run the simulation (uses `risk_scenarios.json` by default)

   python riskscenariostest.py

What this repository contains
- Core scoring pipeline in `riskscenariostest.py` that:
  - builds a role->task reference map
  - computes coverage and weighted risk-reduction per scenario
  - prints ranking, portfolio summary, and presentation talking points

Missing / recommended next steps
- Add `requirements.txt` to pin dependencies (if any packages are introduced).
- Add unit tests covering: `get_required_task_weights`, `compute_scenario_coverage`,
  and `compute_portfolio_summary` so logic is safe and refactorable.
- Improve `riskscenariostest.py` CLI: accept input JSON path and output options
  instead of hard-coded `risk_scenarios.json`.
- Add JSON schema validation (or Pydantic models) for `risk_scenarios.json` to
  catch malformed or incomplete scenario files early.
- Add sample output (example console output or saved JSON) to make results
  easier to verify during demos.
- Add CI (GitHub Actions) to run tests and linting automatically on push/PR.
- Add a `LICENSE` and `CONTRIBUTING.md` for collaboration and reuse guidance.

Implemented enhancements
- Added CLI to `riskscenariostest.py` (`-i/--input`, `-o/--output`, `-q/--quiet`).
- Added Pydantic validation for `risk_scenarios.json` via `schemas.py`.
- Added `requirements.txt` (now includes `pytest` and `pydantic`).
- Added unit tests (`tests/test_scoring.py`, `tests/test_validation.py`).
- Added GitHub Actions CI workflow at `.github/workflows/ci.yml`.
- Added `LICENSE` (MIT) and `CONTRIBUTING.md`.
- The script can save simulation output as JSON using `-o`.

Notes & caveats
- Confirm that the committed `riskscenariostest.py` contains no placeholder
  comments or omitted sections (some copies may include placeholder markers). If
  present, those must be replaced with the real code for the script to run.
- The script currently expects `risk_scenarios.json` in the working directory; a
  CLI flag would allow different paths and safer automation.

If you'd like, I can:
- add a `requirements.txt` and a simple GitHub Actions CI workflow (pytest + lint),
- add unit tests for the scoring functions and a small runner that validates
  `risk_scenarios.json` against a schema, or
- implement a CLI for `riskscenariostest.py` so the input file is configurable.

Contact / author
Project prepared for the CISO practical assignment. Open an issue or ask here
to continue with the next improvements.
