#!/usr/bin/env python3
"""Aggregate grading and timing data across evals into benchmark.json and benchmark.md."""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _utils import read_json, read_config, extract_iteration_num
import os


def validate_snapshot(config_path: Path) -> None:
     """Validate that snapshot exists when mode=improvement.

     Args:
         config_path: Path to workspace/config.json.

     Raises:
         AssertionError: If mode=improvement but no snapshot found.
     """
     config = read_config(config_path)
     if config and config.get("mode") == "improvement":
         workspace_dir = config_path.parent
         snapshot_path = workspace_dir / "skill-snapshot" / "SKILL.md.original"
         assert snapshot_path.exists(), (
             f"ERROR: Improvement mode but no snapshot found at {snapshot_path}!"
         )


def compute_stats(values: list[float]) -> dict[str, float]:
    """Compute mean, stddev, min, max for a list of numeric values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    n = len(values)
    mean = sum(values) / n
    if n > 1:
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0
    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def collect_eval_data(iteration_path: Path) -> list[dict[str, Any]]:
    """Collect grading.json and timing.json from all eval subdirectories."""
    evals = []
    if not iteration_path.exists():
        return evals

    # Find eval directories: iteration-N/eval-ID/
    for entry in sorted(iteration_path.iterdir()):
        if not entry.is_dir() or not entry.name.startswith("eval-"):
            continue

        eval_data: dict[str, Any] = {"eval_id": entry.name}

        # Check for with_skill and without_skill subdirectories
        for config in ["with_skill", "without_skill"]:
            config_dir = entry / config
            grading = read_json(config_dir / "grading.json") if config_dir.exists() else None
            timing = read_json(config_dir / "timing.json") if config_dir.exists() else None

            # Flat-structure fallback: only apply to with_skill to avoid
            # duplicating the same grading data into both configs (zero delta).
            if config == "with_skill":
                if grading is None:
                    grading = read_json(entry / "grading.json")
                if timing is None:
                    timing = read_json(entry / "timing.json")

            eval_data[config] = {
                "grading": grading,
                "timing": timing,
            }

        evals.append(eval_data)

    return evals


def aggregate(evals: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate eval data into benchmark statistics."""
    configs = {"with_skill": {"pass_rates": [], "durations": []},
               "baseline": {"pass_rates": [], "durations": []}}

    for eval_data in evals:
        # with_skill
        ws = eval_data.get("with_skill", {})
        if ws.get("grading") and "pass_rate" in ws["grading"]:
            configs["with_skill"]["pass_rates"].append(ws["grading"]["pass_rate"])
        if ws.get("timing") and "duration_ms" in ws["timing"]:
            configs["with_skill"]["durations"].append(ws["timing"]["duration_ms"])

        # without_skill (baseline)
        bs = eval_data.get("without_skill", {})
        if bs.get("grading") and "pass_rate" in bs["grading"]:
            configs["baseline"]["pass_rates"].append(bs["grading"]["pass_rate"])
        if bs.get("timing") and "duration_ms" in bs["timing"]:
            configs["baseline"]["durations"].append(bs["timing"]["duration_ms"])

    ws_rates = configs["with_skill"]["pass_rates"]
    bs_rates = configs["baseline"]["pass_rates"]
    ws_durs = configs["with_skill"]["durations"]
    bs_durs = configs["baseline"]["durations"]

    delta_pr = (sum(ws_rates) / len(ws_rates) if ws_rates else 0.0) - (sum(bs_rates) / len(bs_rates) if bs_rates else 0.0)
    delta_dur = (sum(ws_durs) / len(ws_durs) if ws_durs else 0.0) - (sum(bs_durs) / len(bs_durs) if bs_durs else 0.0)

    result = {
        "configurations": {
            "with_skill": {
                "pass_rate": compute_stats(configs["with_skill"]["pass_rates"]),
                "duration_ms": compute_stats(configs["with_skill"]["durations"]),
            },
            "baseline": {
                "pass_rate": compute_stats(configs["baseline"]["pass_rates"]),
                "duration_ms": compute_stats(configs["baseline"]["durations"]),
            },
        },
        "delta": {
            "pass_rate": round(delta_pr, 4),
            "duration_ms": round(delta_dur, 4),
        },
        "eval_count": len(evals),
    }

    return result


def generate_markdown(benchmark: dict[str, Any], iteration_num: int) -> str:
    """Generate a human-readable markdown benchmark report."""
    lines = [
        f"# Benchmark Report — Iteration {iteration_num}",
        "",
        "## Summary",
        "",
        "| Metric | With Skill | Baseline | Delta |",
        "|--------|-----------|----------|-------|",
    ]

    ws = benchmark["configurations"]["with_skill"]
    bs = benchmark["configurations"]["baseline"]
    delta = benchmark["delta"]

    # Pass rate row
    ws_pr = ws["pass_rate"]
    bs_pr = bs["pass_rate"]
    pr_delta = delta["pass_rate"]
    pr_sign = "+" if pr_delta >= 0 else ""
    lines.append(
        f"| Pass Rate (mean) | {ws_pr['mean']:.2%} | {bs_pr['mean']:.2%} | {pr_sign}{pr_delta:.2%} |"
    )

    # Duration row
    ws_dur = ws["duration_ms"]
    bs_dur = bs["duration_ms"]
    dur_delta = delta["duration_ms"]
    dur_sign = "+" if dur_delta >= 0 else ""
    lines.append(
        f"| Duration (mean ms) | {ws_dur['mean']:.0f} | {bs_dur['mean']:.0f} | {dur_sign}{dur_delta:.0f} |"
    )

    lines.extend([
        "",
        f"**Evals aggregated:** {benchmark['eval_count']}",
        "",
        "## Detailed Statistics",
        "",
        "### With Skill",
        "",
        "| Metric | Mean | StdDev | Min | Max |",
        "|--------|------|--------|-----|-----|",
        f"| Pass Rate | {ws_pr['mean']:.4f} | {ws_pr['stddev']:.4f} | {ws_pr['min']:.4f} | {ws_pr['max']:.4f} |",
        f"| Duration (ms) | {ws_dur['mean']:.0f} | {ws_dur['stddev']:.0f} | {ws_dur['min']:.0f} | {ws_dur['max']:.0f} |",
        "",
        "### Baseline",
        "",
        "| Metric | Mean | StdDev | Min | Max |",
        "|--------|------|--------|-----|-----|",
        f"| Pass Rate | {bs_pr['mean']:.4f} | {bs_pr['stddev']:.4f} | {bs_pr['min']:.4f} | {bs_pr['max']:.4f} |",
        f"| Duration (ms) | {bs_dur['mean']:.0f} | {bs_dur['stddev']:.0f} | {bs_dur['min']:.0f} | {bs_dur['max']:.0f} |",
        "",
    ])

    # Improvement assessment
    if pr_delta > 0:
        lines.append(f"> **Improvement:** Skill improved pass rate by {pr_delta:.2%} over baseline.")
    elif pr_delta < 0:
        lines.append(f"> **Regression:** Skill decreased pass rate by {abs(pr_delta):.2%} compared to baseline.")
    else:
        lines.append("> **No change:** Pass rate is the same with and without skill.")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: aggregate_benchmark.py <iteration_path>")
        print("  iteration_path: path to iteration-N directory containing eval subdirectories")
        sys.exit(1)

    iteration_path = Path(sys.argv[1])
    if not iteration_path.exists():
        print(f"Error: Path does not exist: {iteration_path}")
        sys.exit(1)

    iteration_num = extract_iteration_num(iteration_path)

    # Collect and aggregate
    evals = collect_eval_data(iteration_path)
    if not evals:
        print(f"No eval directories found in {iteration_path}")
        sys.exit(1)

    benchmark = aggregate(evals)
    benchmark["iteration"] = iteration_num
    benchmark["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Write benchmark.json
    json_path = iteration_path / "benchmark.json"
    json_path.write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    print(f"Written: {json_path}")

    # Write benchmark.md
    md_content = generate_markdown(benchmark, iteration_num)
    md_path = iteration_path / "benchmark.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"Written: {md_path}")

    # Print summary
    ws = benchmark["configurations"]["with_skill"]
    bs = benchmark["configurations"]["baseline"]
    delta = benchmark["delta"]
    print(f"\nSummary: {benchmark['eval_count']} evals aggregated")
    print(f"  With Skill pass rate: {ws['pass_rate']['mean']:.2%}")
    print(f"  Baseline pass rate:   {bs['pass_rate']['mean']:.2%}")
    print(f"  Delta:                {delta['pass_rate']:+.2%}")


if __name__ == "__main__":
    main()
