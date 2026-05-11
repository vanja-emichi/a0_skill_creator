#!/usr/bin/env python3
"""Tests for Task 3: SKILL.md Step 2.1 branching evaluation logic."""

import unittest
from pathlib import Path

SKILL_MD_PATH = Path("/a0/usr/plugins/a0_skill_creator/skills/skill-creator/SKILL.md")


class TestStep21Branching(unittest.TestCase):
    """Test SKILL.md Step 2.1 has branching for new vs improvement mode."""

    @classmethod
    def setUpClass(cls):
        cls.content = SKILL_MD_PATH.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()
        # Extract Phase 2 section for targeted searches
        phase2_start = None
        phase2_end = None
        for i, line in enumerate(cls.lines):
            if "## Phase 2" in line:
                phase2_start = i
            if phase2_start and i > phase2_start and line.startswith("## Phase 3"):
                phase2_end = i
                break
        cls.phase2 = "\n".join(cls.lines[phase2_start:phase2_end]) if phase2_start else ""

    def test_phase2_has_mode_new_path(self):
        """Phase 2 must document mode='new' path with with_skill/without_skill."""
        self.assertIn('mode = "new"', self.phase2)
        idx = self.phase2.index('mode = "new"')
        nearby = self.phase2[idx:idx+1000]
        self.assertIn("with_skill", nearby)
        self.assertIn("without_skill", nearby)

    def test_phase2_has_mode_improvement_path(self):
        """Phase 2 must document mode='improvement' path with new_skill/old_skill."""
        self.assertIn('mode = "improvement"', self.phase2)
        idx = self.phase2.index('mode = "improvement"')
        nearby = self.phase2[idx:idx+1000]
        self.assertIn("new_skill", nearby)
        self.assertIn("old_skill", nearby)

    def test_critical_marker_present(self):
        """CRITICAL marker must be present explaining the difference."""
        self.assertIn("CRITICAL", self.content)

    def test_config_json_read_before_eval(self):
        """Step 2.1 must mention reading config.json to determine mode."""
        step21_start = None
        for i, line in enumerate(self.lines):
            if "Step 2.1" in line:
                step21_start = i
                break
        self.assertIsNotNone(step21_start, "Step 2.1 not found")
        section = "\n".join(self.lines[step21_start:step21_start+5])
        self.assertIn("config.json", section)


if __name__ == "__main__":
    unittest.main()
