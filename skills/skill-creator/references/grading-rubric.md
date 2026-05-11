# Grading Rubric and Assertion Guidelines

Standards for writing eval assertions and grading skill outputs objectively.

---

## Assertion Writing Principles

### Every assertion must be:

1. **Objectively verifiable** — A third party can determine pass/fail without subjective judgment
2. **Specific** — References concrete elements (file names, function signatures, output patterns)
3. **Checkable by inspection** — Can be verified by reading output files, not by running code
4. **Named descriptively** — The assertion text itself describes what is being checked

### Good vs Bad Assertions

| Good Assertion | Why | Bad Assertion | Why |
|---|---|---|---|
| "Output contains a `def process_data` function definition" | Specific, checkable | "Output looks good" | Subjective |
| "The response includes a `try/except` block" | Concrete, verifiable | "Error handling is adequate" | Vague, subjective |
| "All file paths use `Path` objects, not string concatenation" | Specific pattern check | "Code follows best practices" | Undefined criteria |
| "JSON output has `text`, `passed`, and `evidence` fields" | Exact field check | "JSON is valid" | Too broad |
| "The skill description is under 500 characters" | Measurable | "Description is concise" | Subjective |

---

## Assertion Categories

### Category 1: Presence Assertions

Check that specific content exists in the output.

```
"Output contains a Python function definition"
"Response includes installation instructions"
"A markdown table is present in the output"
"The response mentions error handling"
```

### Category 2: Correctness Assertions

Check that content is technically correct.

```
"Function name matches the requested name 'process_data'"
"Import statements use correct module paths"
"Variable names follow snake_case convention"
"The API endpoint path matches the specification"
```

### Category 3: Completeness Assertions

Check that all required elements are present.

```
"All three requested test cases are included"
"Both success and error response formats are documented"
"Configuration options cover all required fields"
"Edge cases for empty input and null values are handled"
```

### Category 4: Format Assertions

Check that output follows expected format.

```
"YAML frontmatter contains 'name' and 'description' fields"
"Code examples use fenced code blocks with language tags"
"File paths use forward slashes, not backslashes"
"JSON output is valid and parseable"
```

### Category 5: Exclusion Assertions

Check that certain content is NOT present.

```
"Output does not contain placeholder text like 'TODO' or 'FIXME'"
"No hardcoded API keys or secrets in the output"
"Response does not include instructions unrelated to the task"
```

---

## Grading Process

### Step 1: Read Assertions

Read all assertions from `eval_metadata.json`. Each assertion is a string describing a verifiable expectation.

### Step 2: Read Output

Read all output files in the eval's output directory. Read the complete content — do not skim.

### Step 3: Evaluate Each Assertion

For each assertion:

1. **Identify the check** — What specific thing needs to be verified?
2. **Search the output** — Find relevant content in the output files
3. **Determine verdict** — PASS or FAIL based on objective evidence
4. **Cite evidence** — Quote the specific text or describe the exact observation

### Step 4: Write grading.json

Output must use exactly these field names:

```json
{
  "expectations": [
    {
      "text": "the assertion text",
      "passed": true,
      "evidence": "quoted evidence from output"
    }
  ],
  "pass_rate": 0.75,
  "summary": "3 of 4 assertions passed"
}
```

**Critical field names:** `text` (not `assertion` or `description`), `passed` (not `result` or `status`), `evidence` (not `reason` or `justification`).

---

## Evidence Standards

### Strong Evidence

- **Direct quotes** from the output (with file name and approximate location)
- **Exact matches** of expected patterns
- **Presence confirmation** with specific text found

Examples:
```
"Found in output.py line 12: 'def process_data(input: str) -> dict:'"
"JSON output contains keys: 'text', 'passed', 'evidence' — matching the required schema"
"Output includes 3 test cases: test_basic, test_edge_case, test_error — all three requested"
```

### Weak Evidence (Avoid)

- Vague references without specifics
- Paraphrasing instead of quoting
- Statements about what is NOT in the output without thorough search

```
"Seems like it's there" — Too vague
"The output looks right" — Subjective
"Error handling probably works" — Unsupported
```

### FAIL Evidence

For failed assertions, evidence should explain WHAT was expected and WHAT was found:

```
"Expected a try/except block handling ValueError, but no exception handling found in the function body"
"Expected function named 'process_data' but found 'handle_data' instead"
"Expected 3 test cases but found only 2: test_basic and test_edge_case"
```

---

## Pass Rate Calculation

```
pass_rate = passed_assertions / total_assertions
```

| Pass Rate | Interpretation |
|-----------|---------------|
| 1.0 | All assertions satisfied — excellent |
| 0.8–0.99 | Minor gaps — review failed assertions |
| 0.5–0.79 | Significant gaps — improvement needed |
| < 0.5 | Major problems — skill likely not working as intended |

---

## Programmatic Assertions

For assertions that can be verified programmatically (not just by reading):

1. Write a small Python check script
2. Run it via `code_execution_tool`
3. Include the script output in the evidence

Example check script:

```python
import json
from pathlib import Path

output = Path('output.txt').read_text()
result = json.loads(output)

# Check field names
assert 'text' in result['expectations'][0], 'Missing text field'
assert 'passed' in result['expectations'][0], 'Missing passed field'
assert 'evidence' in result['expectations'][0], 'Missing evidence field'
print('PASS: All required fields present')
```

The grader should write and run these scripts when applicable, then include the script's output in the evidence field.

---

## Common Grading Mistakes

| Mistake | Correct Approach |
|---|---|
| Grading based on intent rather than output | Grade only what is actually in the output files |
| Giving partial credit | Each assertion is binary: PASS or FAIL |
| Skipping evidence for passes | Every assertion needs evidence, both pass and fail |
| Grading subjectively | If you can't point to specific text, it's not objective |
| Ignoring format requirements | Format assertions count just as much as correctness |
| Being too lenient on near-misses | "Close" is still FAIL for binary assertions |
