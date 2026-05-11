# A0 Skill Creator

Full quality engineering pipeline for creating, evaluating, benchmarking, and iteratively improving Agent Zero skills. Ports Anthropic's skill-creator architecture to Agent Zero's tool model with specialized grader, comparator, and analyzer agent profiles.

## Quick Start

1. Install the plugin into your Agent Zero `usr/plugins/` directory:
   ```bash
   git clone https://github.com/vanja-emichi/a0_skill_creator.git usr/plugins/a0_skill_creator
   ```
2. Restart Agent Zero — the plugin auto-loads.
3. Ask the agent to create or improve a skill:
   > "Create a skill for writing Python unit tests"

## How It Works

The skill-creator runs a **5-phase pipeline** that guides you from intent to a tested, optimized skill:

| Phase | Purpose |
|-------|---------|
| **1. Define & Draft** | Capture intent, detect mode (new/improve), research, write `SKILL.md` |
| **2. Evaluate** | Run test cases, draft assertions, grade results, generate benchmark report |
| **3. Improve** | Apply evaluation feedback, iterate until pass rate ≥ 0.8 (max 5 iterations) |
| **4. Optimize Description** | Tune triggers & descriptions to maximize discoverability and minimize false positives |
| **5. Validate & Deliver** | Final checks, live verification, present the finished skill |

A **fast-path** is also available for quick skills — skip evaluation and go straight from drafting to validation.

## Trigger Phrases

The skill activates when you say things like:

- "create a skill" / "build a skill" / "write a skill"
- "improve skill" / "evaluate skill" / "test skill"
- "optimize skill" / "benchmark skill"
- "modify skill" / "update skill" / "edit skill"

## Project Structure

```
a0_skill_creator/
├── plugin.yaml                         # Plugin manifest
├── skills/
│   └── skill-creator/
│       ├── SKILL.md                     # Main skill instructions
│       ├── references/
│       │   ├── eval-schemas.md          # Evaluation data schemas
│       │   └── grading-rubric.md        # Grading criteria reference
│       └── scripts/
│           ├── _utils.py                # Shared utilities
│           ├── run_loop.py              # Evaluation loop runner
│           ├── aggregate_benchmark.py   # Benchmark aggregation
│           ├── generate_report.py       # Report generation
│           ├── improve_description.py   # Description optimization
│           └── tests/                   # 23 unit tests
│               ├── test_task1_read_config.py
│               ├── test_task2_skill_md_step11.py
│               ├── test_task3_branching_eval.py
│               ├── test_task4_snapshot_validation.py
│               └── test_task5_feedback_mandatory.py
└── agents/                              # Specialized agent profiles
    ├── grader/
    │   ├── agent.yaml
    │   └── prompts/agent.system.main.specifics.md
    ├── comparator/
    │   ├── agent.yaml
    │   └── prompts/agent.system.main.specifics.md
    └── analyzer/
        ├── agent.yaml
        └── prompts/agent.system.main.specifics.md
```

## Agent Profiles

| Profile | Role |
|---------|------|
| **Grader** | Evaluates skill outputs against objective assertions; produces `grading.json` with pass/fail verdicts |
| **Comparator** | Performs blind A/B comparison of skill evaluation outputs without knowing which version produced which |
| **Analyzer** | Examines benchmark data across iterations to identify flaky evaluations, non-discriminating assertions, and improvement patterns |

## Dependencies

- **Agent Zero** — the skill requires the core Agent Zero framework
- **Subordinate profiles**: `grader`, `comparator`, `analyzer` (included), plus `developer` and `researcher` (built-in)
- **Tools used**: `code_execution_tool`, `call_subordinate`, `skills_tool`, `document_query`, `text_editor`

## Running Tests

```bash
python -m pytest skills/skill-creator/scripts/tests/ -v
```

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

## License

MIT
