# Evaluation Data Schemas

JSON schemas for all data artifacts used in the skill evaluation pipeline.

---

## evals.json

Test case definitions. Stored in the workspace root.

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "name": "basic functionality",
      "prompt": "The exact user prompt to test",
      "expected_output": "Human-readable description of what success looks like",
      "files": [],
      "expectations": []
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `skill_name` | string | Name of the skill being evaluated |
| `evals` | array | List of test cases |
| `evals[].id` | integer | Unique test case identifier |
| `evals[].name` | string | Descriptive name for the test case |
| `evals[].prompt` | string | Exact user prompt to execute |
| `evals[].expected_output` | string | Human-readable success description |
| `evals[].files` | array | File paths needed for the test |
| `evals[].expectations` | array | Assertions (filled in Phase 2 Step 2.2) |

---

## eval_metadata.json

Per-eval metadata with assertions. Stored in each `iteration-N/eval-ID/` directory.

```json
{
  "eval_id": 1,
  "eval_name": "basic functionality",
  "prompt": "Create a Python function that...",
  "assertions": [
    "Output contains a valid Python function",
    "Function name matches the requested name",
    "Error handling is included"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `eval_id` | integer | Matches evals.json test case ID |
| `eval_name` | string | Descriptive name |
| `prompt` | string | The exact prompt used |
| `assertions` | array of strings | Verifiable expectations for the grader |

---

## timing.json

Timing data captured after each subordinate run. Stored in each `iteration-N/eval-ID/` directory.

```json
{
  "start_time": "2025-05-11T10:00:00Z",
  "end_time": "2025-05-11T10:02:30Z",
  "duration_ms": 150000,
  "total_tokens": 4500
}
```

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | string | ISO 8601 timestamp when run started |
| `end_time` | string | ISO 8601 timestamp when run completed |
| `duration_ms` | integer | Wall-clock duration in milliseconds |
| `total_tokens` | integer | Total tokens consumed |

---

## grading.json

Grader output for a single eval run. Stored in each `iteration-N/eval-ID/` directory.

**Critical:** Field names must be exactly `text`, `passed`, `evidence`.

```json
{
  "expectations": [
    {
      "text": "Output contains a valid Python function",
      "passed": true,
      "evidence": "Line 12: `def process_data(input: str) -> dict:`"
    },
    {
      "text": "Function name matches the requested name",
      "passed": true,
      "evidence": "Function is named `process_data` matching the request"
    },
    {
      "text": "Error handling is included",
      "passed": false,
      "evidence": "No try/except or validation found in the function body"
    }
  ],
  "pass_rate": 0.667,
  "summary": "2 of 3 assertions passed"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `expectations` | array | Graded assertion results |
| `expectations[].text` | string | The assertion text (from eval_metadata.json) |
| `expectations[].passed` | boolean | Whether the assertion was satisfied |
| `expectations[].evidence` | string | Specific quote or observation supporting the verdict |
| `pass_rate` | float | Fraction of assertions that passed (0.0 to 1.0) |
| `summary` | string | Human-readable summary (e.g., "2 of 3 assertions passed") |

---

## benchmark.json

Aggregated benchmark data across all evals in an iteration. Produced by `aggregate_benchmark.py`. Stored in `iteration-N/` directory.

```json
{
  "iteration": 1,
  "timestamp": "2025-05-11T10:10:00Z",
  "configurations": {
    "with_skill": {
      "pass_rate": {
        "mean": 0.75,
        "stddev": 0.12,
        "min": 0.6,
        "max": 0.9
      },
      "duration_ms": {
        "mean": 150000,
        "stddev": 30000,
        "min": 120000,
        "max": 180000
      }
    },
    "baseline": {
      "pass_rate": {
        "mean": 0.45,
        "stddev": 0.15,
        "min": 0.3,
        "max": 0.6
      },
      "duration_ms": {
        "mean": 140000,
        "stddev": 25000,
        "min": 115000,
        "max": 165000
      }
    }
  },
  "delta": {
    "pass_rate": 0.30,
    "duration_ms": 10000
  },
  "eval_count": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `iteration` | integer | Iteration number |
| `timestamp` | string | ISO 8601 timestamp when benchmark was generated |
| `configurations` | object | Stats for with_skill and baseline runs |
| `configurations.*.pass_rate` | object | Mean, stddev, min, max for pass rates across evals |
| `configurations.*.duration_ms` | object | Mean, stddev, min, max for durations across evals |
| `delta` | object | Difference (with_skill minus baseline) |
| `eval_count` | integer | Number of evals aggregated |

---

## eval_set.json

Trigger evaluation queries for description optimization. Stored in the workspace root.

```json
[
  {"query": "create a new skill", "should_trigger": true},
  {"query": "deploy to production", "should_trigger": false},
  {"query": "build a skill for testing", "should_trigger": true},
  {"query": "write unit tests", "should_trigger": false}
]
```

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Search query to test against `skills_tool:search` |
| `should_trigger` | boolean | Whether the skill should appear in results for this query |

Typically contains 20 queries: 10 should-trigger and 10 should-not-trigger.
Split 60/40 into training and test sets for optimization.

---

## feedback.json

User feedback collected during review. Stored in the workspace root.

```json
{
  "status": "in_progress",
  "reviews": [
    {
      "run_id": "iteration-1/eval-0",
      "feedback": "The skill output missed edge case X. Consider adding...",
      "timestamp": "2025-05-11T10:15:00Z"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Pipeline status: `in_progress`, `needs_improvement`, `accepted` |
| `reviews` | array | Individual review entries |
| `reviews[].run_id` | string | Identifier for the specific eval run |
| `reviews[].feedback` | string | User's feedback text |
| `reviews[].timestamp` | string | ISO 8601 timestamp of the review |

---

## comparison.json

Comparator agent output for blind A/B comparison. Stored in `iteration-N/eval-ID/` directory.

```json
{
  "rubric": [
    {"criterion": "Correctness", "weight": 1.0},
    {"criterion": "Completeness", "weight": 0.8},
    {"criterion": "Clarity", "weight": 0.5}
  ],
  "scores": {
    "A": {"Correctness": 5, "Completeness": 4, "Clarity": 4},
    "B": {"Correctness": 3, "Completeness": 3, "Clarity": 5}
  },
  "verdict": "A",
  "reasoning": "Output A scored higher on correctness and completeness, which are the most important criteria."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `rubric` | array | Comparison criteria with weights |
| `scores` | object | Per-label scores for each criterion (1-5 scale) |
| `verdict` | string | "A" or "B" — which output is better |
| `reasoning` | string | Justification for the verdict |

---

## analysis.json

Analyzer agent output with pattern findings and recommendations. Stored in `iteration-N/` directory.

```json
{
  "non_discriminating_assertions": [
    "Output is non-empty"
  ],
  "flaky_evaluations": [],
  "time_token_tradeoffs": {
    "with_skill_avg_ms": 150000,
    "baseline_avg_ms": 140000,
    "overhead_pct": 7.1,
    "justified": true
  },
  "recommendations": [
    "Replace 'Output is non-empty' with a more discriminating assertion",
    "Consider adding an assertion about error handling for edge cases"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `non_discriminating_assertions` | array | Assertions that always pass or always fail across all runs |
| `flaky_evaluations` | array | Evals with inconsistent results across iterations |
| `time_token_tradeoffs` | object | Analysis of performance differences between configurations |
| `recommendations` | array | Specific improvement suggestions for the skill |
