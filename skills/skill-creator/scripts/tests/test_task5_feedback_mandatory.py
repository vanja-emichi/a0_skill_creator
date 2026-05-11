#!/usr/bin/env python3
"""Tests for Task 5: feedback.json mandatory in SKILL.md Step 3.1."""

import unittest
from pathlib import Path

SKILL_MD_PATH = Path("/a0/usr/plugins/a0_skill_creator/skills/skill-creator/SKILL.md")


class TestFeedbackMandatory(unittest.TestCase):
    """Test SKILL.md Phase 3 Step 3.1 marks feedback.json as MANDATORY."""

    @classmethod
    def setUpClass(cls):
        cls.content = SKILL_MD_PATH.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()
        # Extract Phase 3 section
        p3_start = None
        p3_end = None
        for i, line in enumerate(cls.lines):
            if "## Phase 3" in line:
                p3_start = i
            if p3_start and i > p3_start and line.startswith("## Phase 4"):
                p3_end = i
                break
        cls.phase3 = "\n".join(cls.lines[p3_start:p3_end]) if p3_start else ""

    def test_step31_says_mandatory(self):
        """Step 3.1 should say MANDATORY for feedback.json."""
        self.assertIn("MANDATORY", self.phase3)

    def test_step31_mentions_feedback_json(self):
        """Step 3.1 must mention feedback.json."""
        self.assertIn("feedback.json", self.phase3)

    def test_mandatory_near_feedback(self):
        """MANDATORY should appear near feedback.json in Phase 3."""
        idx = self.phase3.index("feedback.json")
        nearby = self.phase3[max(0, idx-200):idx+200]
        self.assertIn("MANDATORY", nearby)

    def test_step31_has_example_json(self):
        """Step 3.1 should include example feedback.json structure."""
        self.assertIn("status", self.phase3)
        self.assertIn("reviews", self.phase3)


if __name__ == "__main__":
    unittest.main()
