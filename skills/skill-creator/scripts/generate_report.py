#!/usr/bin/env python3
"""Generate a markdown evaluation report from benchmark and grading data."""

import json
import sys
from pathlib import Path
from typing import Any

from _utils import read_json, extract_iteration_num, extract_eval_num, escape_markdown_table


def format_pass_rate(rate: float) -> str:
    """Format a pass rate as a percentage string."""
    return f"{rate:.0%}" if rate == int(rate) else f"{rate:.1%}"


def generate_summary_section(benchmark: dict[str, Any]) -> list[str]:
    """Generate the summary comparison table."""
    lines = [
        "## Summary",
        "",
        "| Metric | With Skill | Baseline | Delta |",
        "|--------|-----------|----------|-------|",
    ]

    ws = benchmark.get("configurations", {}).get("with_skill", {})
    bs = benchmark.get("configurations", {}).get("baseline", {})
    delta = benchmark.get("delta", {})

    ws_pr = ws.get("pass_rate", {})
    bs_pr = bs.get("pass_rate", {})
    pr_delta = delta.get("pass_rate", 0)
    pr_sign = "+" if pr_delta >= 0 else ""
    lines.append(
        f"| Pass Rate | {format_pass_rate(ws_pr.get('mean', 0))} | "
        f"{format_pass_rate(bs_pr.get('mean', 0))} | {pr_sign}{format_pass_rate(pr_delta)} |"
    )

    ws_dur = ws.get("duration_ms", {})
    bs_dur = bs.get("duration_ms", {})
    dur_delta = delta.get("duration_ms", 0)
    dur_sign = "+" if dur_delta >= 0 else ""
    lines.append(
        f"| Avg Duration | {ws_dur.get('mean', 0):.0f}ms | "
        f"{bs_dur.get('mean', 0):.0f}ms | {dur_sign}{dur_delta:.0f}ms |"
    )

    lines.append("")
    return lines


def generate_eval_breakdown(iteration_path: Path) -> list[str]:
    """Generate per-eval breakdown with prompts, assertions, and grades."""
    lines = ["## Per-Eval Breakdown", ""]

    eval_dirs = sorted(
        [d for d in iteration_path.iterdir() if d.is_dir() and d.name.startswith("eval-")],
        key=extract_eval_num,
    )

    if not eval_dirs:
        lines.append("_No eval directories found._")
        lines.append("")
        return lines

    for eval_dir in eval_dirs:
        eval_id = eval_dir.name
        metadata = read_json(eval_dir / "eval_metadata.json")

        lines.append(f"### {eval_id}")

        if metadata:
            eval_name = escape_markdown_table(metadata.get("eval_name", "unnamed"))
            prompt = escape_markdown_table(metadata.get("prompt", ""))
            lines.append(f"**Name:** {eval_name}")
            lines.append(f"**Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
            lines.append("")

        # Grading for with_skill
        ws_grading = read_json(eval_dir / "with_skill" / "grading.json")
        bs_grading = read_json(eval_dir / "without_skill" / "grading.json")

        # Also check flat structure
        if ws_grading is None:
            ws_grading = read_json(eval_dir / "grading.json")

        for label, grading in [("With Skill", ws_grading), ("Baseline", bs_grading)]:
            if grading:
                pr = grading.get("pass_rate", 0)
                summary = escape_markdown_table(grading.get("summary", ""))
                lines.append(f"**{label}:** {summary} (pass rate: {format_pass_rate(pr)})")
                lines.append("")

                expectations = grading.get("expectations", [])
                if expectations:
                    lines.append("| Assertion | Result | Evidence |")
                    lines.append("|-----------|--------|----------|")
                    for exp in expectations:
                        text = escape_markdown_table(exp.get("text", ""))
                        passed = "\u2705 PASS" if exp.get("passed") else "\u274c FAIL"
                        evidence = escape_markdown_table(exp.get("evidence", ""))
                        if len(evidence) > 80:
                            evidence = evidence[:77] + "..."
                        lines.append(f"| {text} | {passed} | {evidence} |")
                    lines.append("")

        # Timing
        ws_timing = read_json(eval_dir / "with_skill" / "timing.json")
        bs_timing = read_json(eval_dir / "without_skill" / "timing.json")
        if ws_timing is None:
            ws_timing = read_json(eval_dir / "timing.json")

        if ws_timing or bs_timing:
            lines.append("**Timing:**")
            if ws_timing:
                lines.append(f"- With Skill: {ws_timing.get('duration_ms', 0):.0f}ms, {ws_timing.get('total_tokens', 0)} tokens")
            if bs_timing:
                lines.append(f"- Baseline: {bs_timing.get('duration_ms', 0):.0f}ms, {bs_timing.get('total_tokens', 0)} tokens")
            lines.append("")

    return lines


def generate_analysis_section(iteration_path: Path) -> list[str]:
    """Generate the analysis and recommendations section."""
    analysis = read_json(iteration_path / "analysis.json")
    if not analysis:
        return []

    lines = ["## Analysis & Recommendations", ""]

    non_disc = analysis.get("non_discriminating_assertions", [])
    if non_disc:
        lines.append("### Non-Discriminating Assertions")
        lines.append("")
        lines.append("These assertions always pass or always fail — they don't distinguish skill quality:")
        lines.append("")
        for a in non_disc:
            lines.append(f"- {escape_markdown_table(str(a))}")
        lines.append("")

    flaky = analysis.get("flaky_evaluations", [])
    if flaky:
        lines.append("### Flaky Evaluations")
        lines.append("")
        lines.append("These evaluations show inconsistent results across runs:")
        lines.append("")
        for f in flaky:
            lines.append(f"- {escape_markdown_table(str(f))}")
        lines.append("")

    tradeoffs = analysis.get("time_token_tradeoffs", {})
    if tradeoffs:
        lines.append("### Performance Tradeoffs")
        lines.append("")
        ws_ms = tradeoffs.get("with_skill_avg_ms", 0)
        bs_ms = tradeoffs.get("baseline_avg_ms", 0)
        overhead = tradeoffs.get("overhead_pct", 0)
        justified = tradeoffs.get("justified", False)
        lines.append(f"- With Skill avg: {ws_ms:.0f}ms")
        lines.append(f"- Baseline avg: {bs_ms:.0f}ms")
        lines.append(f"- Overhead: {overhead:.1f}%")
        lines.append(f"- Justified: {'Yes' if justified else 'No'}")
        lines.append("")

    recs = analysis.get("recommendations", [])
    if recs:
        lines.append("### Recommendations")
        lines.append("")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {escape_markdown_table(str(r))}")
        lines.append("")

    return lines


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <iteration_path>")
        print("  iteration_path: path to iteration-N directory")
        sys.exit(1)

    iteration_path = Path(sys.argv[1])
    if not iteration_path.exists():
        print(f"Error: Path does not exist: {iteration_path}")
        sys.exit(1)

    # Extract iteration number
    iteration_num = extract_iteration_num(iteration_path)

    # Load benchmark data
    benchmark = read_json(iteration_path / "benchmark.json")

    # Build report
    lines = [
        f"# Evaluation Report — Iteration {iteration_num}",
        "",
    ]

    if benchmark:
        lines.extend(generate_summary_section(benchmark))
    else:
        lines.append("_No benchmark data available._")
        lines.append("")

    lines.extend(generate_eval_breakdown(iteration_path))
    lines.extend(generate_analysis_section(iteration_path))

    # Write report
    report_path = iteration_path / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written: {report_path}")


if __name__ == "__main__":
    main()
