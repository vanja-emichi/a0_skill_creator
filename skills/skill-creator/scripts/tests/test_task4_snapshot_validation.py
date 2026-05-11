#!/usr/bin/env python3
"""Tests for Task 4: Snapshot validation in aggregate_benchmark.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _utils import read_config


class TestSnapshotValidation(unittest.TestCase):
    """Test aggregate_benchmark validates snapshot when mode=improvement."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpdir_path = Path(self.tmpdir)

    def _setup_iteration_dir(self, mode, with_snapshot=False):
        """Create a minimal iteration directory with config and eval data."""
        # Create workspace config
        workspace = self.tmpdir_path / "workspace"
        workspace.mkdir(exist_ok=True)
        config = {
            "mode": mode,
            "base_skill_path": "/path/to/skill/SKILL.md",
            "skill_name": "test-skill",
            "iteration": 1,
        }
        (workspace / "config.json").write_text(json.dumps(config), encoding="utf-8")

        # Create snapshot if requested
        if with_snapshot:
            snapshot_dir = workspace / "skill-snapshot"
            snapshot_dir.mkdir(exist_ok=True)
            (snapshot_dir / "SKILL.md.original").write_text("# original", encoding="utf-8")

        # Create iteration-1 with eval-0
        iteration = workspace / "iteration-1"
        iteration.mkdir(exist_ok=True)
        eval_dir = iteration / "eval-0"
        eval_dir.mkdir(exist_ok=True)

        # Create grading and timing in with_skill
        ws_dir = eval_dir / "with_skill"
        ws_dir.mkdir(exist_ok=True)
        grading = {"expectations": [{"text": "test", "passed": True, "evidence": "ok"}], "pass_rate": 1.0, "summary": "1 of 1"}
        (ws_dir / "grading.json").write_text(json.dumps(grading), encoding="utf-8")
        timing = {"start_time": "2025-01-01T00:00:00Z", "end_time": "2025-01-01T00:01:00Z", "duration_ms": 60000, "total_tokens": 1000}
        (ws_dir / "timing.json").write_text(json.dumps(timing), encoding="utf-8")

        # without_skill
        bs_dir = eval_dir / "without_skill"
        bs_dir.mkdir(exist_ok=True)
        (bs_dir / "grading.json").write_text(json.dumps(grading), encoding="utf-8")
        (bs_dir / "timing.json").write_text(json.dumps(timing), encoding="utf-8")

        return workspace

    def test_new_mode_no_snapshot_succeeds(self):
        """New mode should work without a snapshot."""
        from aggregate_benchmark import aggregate, collect_eval_data
        workspace = self._setup_iteration_dir("new", with_snapshot=False)
        iteration_path = workspace / "iteration-1"
        evals = collect_eval_data(iteration_path)
        self.assertGreater(len(evals), 0)
        result = aggregate(evals)
        self.assertIn("configurations", result)

    def test_improvement_mode_with_snapshot_succeeds(self):
        """Improvement mode should work when snapshot exists."""
        from aggregate_benchmark import aggregate, collect_eval_data
        workspace = self._setup_iteration_dir("improvement", with_snapshot=True)
        iteration_path = workspace / "iteration-1"
        evals = collect_eval_data(iteration_path)
        self.assertGreater(len(evals), 0)
        result = aggregate(evals)
        self.assertIn("configurations", result)

    def test_improvement_mode_without_snapshot_raises(self):
        """Improvement mode without snapshot should raise an error."""
        from aggregate_benchmark import validate_snapshot
        workspace = self._setup_iteration_dir("improvement", with_snapshot=False)
        config_path = workspace / "config.json"
        with self.assertRaises(AssertionError):
            validate_snapshot(config_path)

    def test_new_mode_validate_snapshot_ok(self):
        """New mode validate_snapshot should not raise even without snapshot."""
        from aggregate_benchmark import validate_snapshot
        workspace = self._setup_iteration_dir("new", with_snapshot=False)
        config_path = workspace / "config.json"
        # Should not raise
        validate_snapshot(config_path)


if __name__ == "__main__":
    unittest.main()
