# CISO Practical Assignment Report

## Project Overview

This repository implements a decision-support simulation for cybersecurity risk
scenarios.  It evaluates how a proposed hiring and upskilling plan covers
critical tasks defined by the NICE framework, calculates weighted task coverage,
and produces risk reduction metrics for each scenario and for the overall
portfolio.

The work supports a practical assignment in the "Dirección y Gestión de la
Ciberseguridad" course, dated February 2026.

## Key Deliverables

1. **Core simulation script** (`riskscenariostest.py`) with functions to:
   - build entity-to-task maps
   - compute scenario coverage using required tasks and claimed role coverage
   - rank scenarios and calculate portfolio summaries
   - provide CLI options for input, output, and quiet mode

2. **Data files** including a sample `risk_scenarios.json` and a role-costs
   catalogue. Two reference PDFs from NICE were also included.

3. **Schema validation** with Pydantic models (`schemas.py`) to ensure input
   JSON conforms to expected structure.

4. **Testing infrastructure** using `pytest` with unit tests for both scoring
   logic and schema validation (`tests/`).

5. **Continuous integration** configuration (`.github/workflows/ci.yml`) running
   the test suite on pushes and pull requests.

6. **Documentation**: comprehensive README, a contributions guide, a license,
   and an example output JSON.

7. **Quality enhancements** over time, such as CLI argument support, floating-
   point tolerant tests, and workspace settings to avoid IDE warnings.

## Implementation Details

- **Design**: functions are pure and easily testable. Coverage evaluation is
  decoupled from I/O, enabling offline testing. Risk reduction uses weighted
  sums and modifiers.

- **Validation**: JSON schema implemented via Pydantic ensures early feedback
  on malformed scenario files.

- **Testing**: edge cases considered, including tasks not covered, invalid
  role claims, and missing weights. Floating point comparisons use
  `pytest.approx`.

- **CLI**: simple argument parsing with `argparse` allows specifying an input
  file, optional output path, and quiet mode. Output can be serialized back to
  JSON for further analysis.

- **CI/Workflow**: GitHub Actions script sets up Python 3.11, installs
  requirements, and runs the tests. Workspace settings disable intrusive YAML
  language server diagnostics.

## Execution Summary

- Environment: Windows 11, Python 3.12 (virtual environment recommended).
- Run `python riskscenariostest.py` to execute with default data. Add `-i` and
  `-o` flags for custom files.
- Available unit tests exercise core functions; `pytest -q` executes the suite.
- Example simulation output is stored in `example_simulation_output.json`.

## Lessons and Reflections

- Starting with a minimal prototype and iterating with tests greatly improved
  confidence and maintainability.
- Schema validation prevented runtime errors when working with complex JSON
  structures.
- Handling editor diagnostics (YAML language server) required workspace
  configuration, illustrating the value of environment-specific settings.

## Future Work

- Extend the scoring model with additional attributes such as skills or
  knowledge weights.
- Integrate with a web front-end or automated report generator.
- Add more comprehensive scenario editing tools and JSON schema documentation.
- Introduce linting/formatting (e.g., `ruff`, `black`) in the CI pipeline.

---

Report generated March 1, 2026.  Prepared by the project developer during the
CISO practical assignment.
