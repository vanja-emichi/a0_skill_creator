---
name: skill-creator
description: Create, evaluate, benchmark, and iteratively improve Agent Zero skills through a structured quality pipeline. Use when the user asks to create, improve, modify, update, or edit any SKILL.md file or skill directory. Also use when the user approves a design proposal for skill changes ("do it", "implement", "go ahead") — the pipeline must run. Triggers on any mention of skill creation, modification, evaluation, quality, benchmarking, or optimization.

trigger_patterns:
  - create a skill
  - build a skill
  - new skill
  - improve skill
  - evaluate skill
  - test skill
  - skill creator
  - skill quality
  - optimize skill
  - benchmark skill
  - skill evaluation
  - write a skill
  - modify skill
  - update skill
  - edit skill
  - change skill
  - add to skill
  - skill improvement
  - skill enhancement
  - skill needs
  - skill should have
  - implement skill
  - SKILL.md
  - skill pipeline
  - skill changes

tags:
  - skills
  - evaluation
  - quality
  - benchmarking
---

# Skill Creator

A full quality engineering pipeline for creating, evaluating, benchmarking, and iteratively improving Agent Zero skills. Ports Anthropic's skill-creator architecture to Agent Zero's tool model.

Absorbs and supersedes the `build-skill` skill. When this skill is loaded, follow its pipeline instead of the simpler `build-skill` workflow.

## Interactive Coach Behavior

When invoked, detect where the user is in the pipeline:

1. **New request** — start at Phase 1 Step 1.1
2. **"Continue" or "keep going"** — resume from the last completed step
3. **"Improve skill at path X"** — start at Phase 1 Step 1.1 with improvement mode
4. **"Just write a quick skill"** — skip to Fast-Path
5. **"Do it" / "implement" / "go ahead" after design discussion** — The agent proposed changes and the user approved. This is NOT permission to skip the pipeline. Start at Phase 1 Step 1.1 with `mode='improvement'` and run the full pipeline.

Ask clarifying questions only when essential. Default to action.

## Pipeline Mode Enforcement

> **⚠️ HARD GATE: ANY edit to a managed skill file REQUIRES Phase 2 before presenting results as complete.**

Before editing a skill file that is under pipeline management (any skill with a `workspace/` directory or existing pipeline configuration), the agent MUST:

1. **Announce:** "I am about to edit [skill name] in [mode] mode, starting iteration [N]. Pipeline will run."
2. **If uncertain about scope,** ask the user: "This change affects [X]. Should I run the full evaluation pipeline, or is this a minor fix (<10 lines, no structural change)?"
3. **After editing,** run Phase 2 evaluation before presenting results as complete.

**This gate has NO exceptions for improvement mode.** In `mode='new'`, fast-path may apply. In `mode='improvement'`, the pipeline ALWAYS runs.

---

## Phase 1: Skill Definition and Drafting

### Step 1.1: Capture Intent and Detect Mode

Extract answers to four questions before writing anything:
1. What should the skill enable the agent to do?
2. When should the skill trigger?
3. What is the expected output format?
4. Should test cases be set up? (Skills with subjective outputs may skip evals)

**MODE DETECTION (MANDATORY):** Immediately after capturing intent, explicitly determine the pipeline mode:

```json
{
  "mode": "new" | "improvement",
  "base_skill_path": "/path/to/skill/SKILL.md",
  "skill_name": "skill-name",
  "iteration": 1
}
```

Save this as `workspace/config.json`. **This step is NOT optional.** Every run must have explicit mode detection.

**Mode determination rules:**
- If user says "improve skill at path X" or "make skill X better" → `mode = "improvement"`
- If user says "create a new skill" or no existing skill is mentioned → `mode = "new"`
- If the skill already exists on disk and user is asking for changes → `mode = "improvement"`
- Mode can change during a session: iteration 1 may be `"new"`, iteration 2+ becomes `"improvement"`

**If mode = "improvement" — SNAPSHOT (MANDATORY CHECKPOINT):**

1. Copy the **entire skill directory** (SKILL.md + scripts/ + references/ + assets/) to `workspace/skill-snapshot/`
2. Verify snapshot exists:
   ```bash
   ls workspace/skill-snapshot/SKILL.md.original
   ```
3. **DO NOT proceed to Phase 2 until snapshot is verified.** This is a hard gate.

**If mode = "new" — no snapshot needed.**

Fast-path: If user says "just write a quick skill", skip to Step 1.3 + Step 5.1 only (write + validate).

### Step 1.2: Interview and Research

Ask about edge cases, formats, dependencies as needed.

- Use `call_subordinate(profile='researcher')` for domain research
- Use `skills_tool:search` to check for similar existing skills
- Read relevant source docs via `document_query` or `deep_wiki`

Do not over-research. Move to writing when intent is clear.

### Step 1.3: Write SKILL.md

Draft the skill following Agent Zero conventions:

**Directory structure:**
```
skill-name/
├── SKILL.md
├── scripts/      # optional deterministic helpers
├── references/   # optional details loaded only when needed
└── assets/       # optional output resources or templates
```

**Frontmatter** (use `trigger_patterns` for discoverability):
```yaml
---
name: skill-name
description: Create, evaluate, benchmark, and iteratively improve Agent Zero skills through a structured quality pipeline. Use when the user asks to create, improve, modify, update, or edit any SKILL.md file or skill directory. Also use when the user approves a design proposal for skill changes ("do it", "implement", "go ahead") — the pipeline must run. Triggers on any mention of skill creation, modification, evaluation, quality, benchmarking, or optimization.

trigger_patterns:
  - create a skill
  - build a skill
  - new skill
  - improve skill
  - evaluate skill
  - test skill
  - skill creator
  - skill quality
  - optimize skill
  - benchmark skill
  - skill evaluation
  - write a skill
  - modify skill
  - update skill
  - edit skill
  - change skill
  - add to skill
  - skill improvement
  - skill enhancement
  - skill needs
  - skill should have
  - implement skill
  - SKILL.md
  - skill pipeline
  - skill changes

tags:
  - relevant-tag
---
```

**Body rules:**
- Under 500 lines
- Clear headers, procedural instructions
- 2-3 examples
- Move long material to `references/`
- No README, changelog, or install guide

**Placement:** Plugin-scoped for plugin-owned tools, root `skills/` for framework workflows.

**Frontmatter patching rules:**
- When patching frontmatter, ensure no duplicate YAML fields (e.g., two `tags:` lines)
- Read the current frontmatter first, then replace fields completely
- Use `text_editor:patch` with the full frontmatter block

**Validate:**
```python
python3 -c "from helpers.skills import validate_skill_md; from pathlib import Path; print(validate_skill_md(Path('path/to/SKILL.md')))"
```

### Step 1.4: Write Test Cases

Create 2-3 realistic test prompts in workspace `evals/evals.json`:

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "name": "basic functionality",
      "prompt": "The exact user prompt to test",
      "expected_output": "What success looks like",
      "files": [],
      "expectations": []
    }
  ]
}
```

Leave `expectations` empty — they will be drafted in Step 2.2.

---

## Phase 2: Running and Evaluating
 
 **Model Presets:** Before running evaluations, read the user's model presets:
 
 ```bash
 cat /a0/usr/plugins/_model_config/presets.yaml
 ```
 
 **CRITICAL: You MUST use the EXACT `provider` and `name` values from presets.yaml.**
 Do NOT invent providers (e.g., `openrouter`) or model names (e.g., `anthropic/claude-sonnet-4`).
 The user's presets define the only valid provider and model name combinations.
 For example, if presets show `provider: a0_venice` and `name: claude-sonnet-4-6`,
 you MUST use those exact values — never substitute or guess.
 If you reference model configuration anywhere in skill output, agent profiles, or
 eval scripts, the values must come from this file.
 
 If presets exist, ask the user which model to use for evaluation runs.
 Different models may produce different results — testing across multiple presets
 improves skill robustness. To use a specific preset, the user must activate it
 in Settings before running evals. Subordinates inherit the active model config.
 

### Step 2.1: Run Evaluations

**Read `workspace/config.json` to determine mode.** This changes the evaluation strategy:

**If mode = "new":**
1. **With-skill:** `call_subordinate(profile='developer')`
   - Message: "Load skill at path X, then execute this prompt: Y"
   - Save output to `workspace/iteration-N/eval-ID/with_skill/outputs/`
2. **Baseline (no skill):** `call_subordinate(profile='developer')`
   - Message: "Execute this prompt: Y" (no skill loaded)
   - Save output to `workspace/iteration-N/eval-ID/without_skill/outputs/`

**If mode = "improvement":**
1. **New skill:** `call_subordinate(profile='developer')`
   - Message: "Load skill at path X (the UPDATED skill), then execute this prompt: Y"
   - Save output to `workspace/iteration-N/eval-ID/new_skill/outputs/`
2. **Old skill:** `call_subordinate(profile='developer')`
   - Message: "Load skill from workspace/skill-snapshot/SKILL.md.original, then execute this prompt: Y"
   - Save output to `workspace/iteration-N/eval-ID/old_skill/outputs/`

**CRITICAL:** For improvement mode, BOTH runs use a skill. The comparison is
old-skill vs new-skill, NOT skill vs no-skill. This measures incremental improvement.

**Workspace structure:**
```
skill-name-workspace/
├── config.json                    # Mode tracking (new vs improvement)
├── skill-snapshot/                # Created when mode=improvement
│   ├── SKILL.md.original
│   ├── scripts/
│   ├── references/
│   └── assets/
├── iteration-1/
│   ├── eval-0/
│   │   ├── [with_skill|new_skill]/outputs/
│   │   ├── [without_skill|old_skill]/outputs/
│   │   ├── eval_metadata.json
│   │   ├── timing.json
│   │   └── grading.json
│   └── benchmark.json
├── evals/evals.json
├── eval_set.json
└── feedback.json
```

### Step 2.2: Draft Assertions

Draft verifiable expectations for each test case:

- Objectively verifiable (not requiring subjective judgment)
- Named descriptively
- Checkable by inspection

For programmatically verifiable assertions: write and run check scripts.

Update `evals.json` expectations and create `eval_metadata.json`:

```json
{
  "eval_id": 1,
  "eval_name": "basic functionality",
  "prompt": "...",
  "assertions": ["assertion 1", "assertion 2"]
}
```

See grading rubric for assertion writing guidelines:
§§include(/a0/usr/plugins/a0_skill_creator/skills/skill-creator/references/grading-rubric.md)

### Step 2.3: Capture Timing

Record `timing.json` immediately after each subordinate completes:

```json
{
  "start_time": "2025-05-11T10:00:00Z",
  "end_time": "2025-05-11T10:02:30Z",
  "duration_ms": 150000,
  "total_tokens": 4500
}
```

### Step 2.4: Grade

`call_subordinate(profile='grader')` with:
- Path to assertions (`eval_metadata.json`)
- Path to output directory
- Instructions to write `grading.json`

Grader produces `grading.json`:
```json
{
  "expectations": [
    {"text": "assertion text", "passed": true, "evidence": "quote from output"}
  ],
  "pass_rate": 0.75,
  "summary": "3 of 4 assertions passed"
}
```

**Critical:** Field names must be exactly `text`, `passed`, `evidence`.

### Step 2.5: Compare (Optional)

`call_subordinate(profile='comparator')` for rigorous improvement comparisons:
- Send both outputs labeled A and B (randomize order)
- Comparator generates rubric and judges without knowing labels
- Produces `comparison.json`

### Step 2.6: Analyze

`call_subordinate(profile='analyzer')` for post-hoc analysis:
- Reads benchmark data and grading results
- Identifies non-discriminating assertions, flaky evaluations
- Analyzes time/token tradeoffs
- Produces `analysis.json` with recommendations

### Step 2.7: Aggregate and Report

Run aggregation via `code_execution_tool`:

```bash
python3 /a0/usr/plugins/a0_skill_creator/skills/skill-creator/scripts/aggregate_benchmark.py workspace/iteration-N
```

Then generate the report:

```bash
python3 /a0/usr/plugins/a0_skill_creator/skills/skill-creator/scripts/generate_report.py workspace/iteration-N
```

Present `report.md` to user via `document_query` for review.

---

## Phase 3: Improving the Skill

### Step 3.1: Capture Feedback

Create or update `workspace/feedback.json` — this is MANDATORY, not optional:

```json
{
  "status": "in_progress",
  "reviews": [
    {"run_id": "iteration-1/eval-0", "feedback": "...", "timestamp": "..."}
  ]
}
```

Collect:
- User's verbal feedback from report review
- Analyzer recommendations
- Grader evidence for failed assertions

### Step 3.2: Apply Improvements

Revise SKILL.md **in-place at its current location** — never duplicate or copy the skill to a new directory. The skill already lives somewhere on disk. Always edit that original file directly.

**Improvement principles:**
- Generalize specific patterns
- Keep instructions lean
- Explain WHY, not just WHAT
- Bundle repeated work into references
- Add scripts for deterministic operations

**Structural Change Guard:**

After applying improvements, assess the change magnitude:

| Change Type | Examples | Phase 2 Required? |
|---|---|---|
| **Structural** | New phases, new files, new scripts, >50 lines changed, new references/ | **YES — full Phase 2 mandatory** |
| **Minor** | Typo fixes, wording tweaks, <10 lines, no structural change | Phase 2 may be skipped ONLY if user explicitly approves |

> **Rule:** When in doubt, run Phase 2. It is always safer to evaluate than to skip.

### Step 3.3: Iterate

Create `iteration-N+1`, return to Phase 2 Step 2.1.

Continue until:
- Pass rate meets target (≥ 0.8)
- User is satisfied
- Max iterations reached (default: 5)

---

## Phase 4: Description Optimization

### Step 4.1: Generate Trigger Eval Queries

Generate 20 trigger evaluation queries:
- 10 should-trigger (skill SHOULD appear)
- 10 should-not-trigger (skill should NOT appear)

**Anti-false-positive guidance:** should-not-trigger queries should include:
- Similar but different tasks (e.g., "create a plugin" when skill creates agents)
- Related but distinct operations (e.g., "review code" vs "create skill")
- Broader tasks where skill is only a small part

Save to `workspace/eval_set.json`:
```json
[
  {"query": "create a new skill", "should_trigger": true},
  {"query": "deploy to production", "should_trigger": false}
]
```

Present to user for review and editing.

### Step 4.2: Train/Test Split

Split using helper function via `code_execution_tool`:

```python
import sys
sys.path.insert(0, '/a0/usr/plugins/a0_skill_creator/skills/skill-creator/scripts')
from run_loop import split_eval_set, load_eval_set

eval_set = load_eval_set('workspace/eval_set.json')
train, test = split_eval_set(eval_set, holdout=0.4)
print(f"Train: {len(train)}, Test: {len(test)}")
```

### Step 4.3: Run Optimization Loop

The agent orchestrates the loop itself using helper functions from `run_loop.py` and `improve_description.py`.

Each iteration:
1. Test current triggers via `skills_tool:search` for each query (3 runs per query)
2. Score results using `score_trigger_results()` from `run_loop.py`
3. If training queries fail → use `format_improvement_prompt()` to construct improvement prompt
4. Parse agent output using `extract_improvement()` from `improve_description.py`
5. If description > 1024 chars → use `format_shortening_request()` for follow-up
6. Store results in history
7. Max 5 iterations, `trigger_threshold=0.5`

### Step 4.4: Apply Best Result

Select best using `select_best_description()` — optimized for **test set** score (not train).

Update the skill's SKILL.md frontmatter **in-place** at its current location. Update `description` and `trigger_patterns` fields.

---

## Phase 5: Validate and Deliver

### Step 5.1: Final Validation

```python
python3 -c "from helpers.skills import validate_skill_md; from pathlib import Path; print(validate_skill_md(Path('path/to/SKILL.md')))"
```

Must return empty issues list.

### Step 5.2: Live Path Verification

1. Ask a short prompt that should discover the skill → confirm `skills_tool:search` returns it
2. Load via `skills_tool:load`
3. Confirm the agent follows the skill's instructions on a median prompt

### Step 5.3: Present Summary

Present to user:
- Name, description, triggers, tags
- Location on disk
- Eval results (pass rate, benchmark summary)
- Number of iterations
- Trigger optimization score (if Phase 4 ran)

---

## Fast-Path ("Just Write a Quick Skill")

When user says "just write a quick skill" or "quickly create a skill for X":

1. **Capture intent** (Step 1.1) — brief, 1-2 questions max
2. **Write SKILL.md** (Step 1.3) — draft and validate
3. **Validate** (Step 5.1) — run `validate_skill_md()`

Skip all evaluation, benchmarking, and optimization phases.

> **⚠️ PROHIBITION:** Fast-path applies ONLY to brand-new skills in `mode='new'`. NEVER use fast-path for improvements to existing skills, regardless of how simple the request seems. If `config.json` has `mode='improvement'`, the full pipeline MUST run.

---

## Available Agent Profiles

| Profile | Purpose | Invocation |
|---------|---------|------------|
| `grader` | Evaluate assertions against outputs | `call_subordinate(profile='grader')` |
| `comparator` | Blind A/B comparison | `call_subordinate(profile='comparator')` |
| `analyzer` | Benchmark analysis + recommendations | `call_subordinate(profile='analyzer')` |

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `aggregate_benchmark.py` | Aggregate grading + timing → benchmark.json + .md | `python3 scripts/aggregate_benchmark.py <iteration_path>` |
| `generate_report.py` | Generate markdown review report | `python3 scripts/generate_report.py <iteration_path>` |
| `run_loop.py` | Optimization loop helpers | Import functions via `code_execution_tool` |
| `improve_description.py` | Parse/validate improved triggers + description | Import functions via `code_execution_tool` |

## Key Principles

- **Edit skills in-place** — never duplicate or copy to a new directory
- **Use `trigger_patterns`** — scores 9pts for exact match, higher than description alone
- **Record timing immediately** — capture timing.json right after subordinate completes
- **Binary grading** — each assertion is PASS or FAIL, no partial credit
- **Blind comparison** — never tell the comparator which output is which
- **Test-set selection** — always select best description by test set, not train set
- **Max 5 iterations** — prevent infinite loops in improvement and optimization
- **Pipeline is mandatory** — any edit to a skill file under pipeline management MUST be followed by Phase 2 evaluation before presenting results as complete
- **Design discussions are pre-pipeline** — design discussions, proposals, and user approvals are NOT pipeline steps; they are pre-pipeline conversations that MUST lead into the pipeline
