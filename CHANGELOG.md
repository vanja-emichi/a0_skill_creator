# Changelog

All notable changes to the A0 Skill Creator plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-05-11

### Added
- 5-phase skill creation pipeline (Define → Evaluate → Improve → Optimize → Deliver)
- Fast-path mode for quick skill creation without evaluation
- `skill-creator` skill with full `SKILL.md` instructions
- Specialized agent profiles:
  - **Grader** — evaluates outputs against objective assertions
  - **Comparator** — blind A/B comparison of skill versions
  - **Analyzer** — benchmark analysis across iterations
- Evaluation scripts:
  - `run_loop.py` — evaluation loop runner
  - `aggregate_benchmark.py` — benchmark data aggregation
  - `generate_report.py` — report generation
  - `improve_description.py` — trigger/description optimization
  - `_utils.py` — shared utilities
- Reference documentation:
  - `eval-schemas.md` — evaluation data schemas
  - `grading-rubric.md` — grading criteria reference
- Unit test suite (23 tests covering config, mode detection, branching eval, snapshot validation, feedback)
- Plugin manifest (`plugin.yaml`)
