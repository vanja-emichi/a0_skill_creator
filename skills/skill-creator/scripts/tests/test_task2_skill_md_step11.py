#!/usr/bin/env python3
"""Tests for Task 2: SKILL.md Step 1.1 mode detection and snapshot checkpoint."""

import unittest
from pathlib import Path

SKILL_MD_PATH = Path("/a0/usr/plugins/a0_skill_creator/skills/skill-creator/SKILL.md")


class TestSkillMdStep11(unittest.TestCase):
    """Test SKILL.md Step 1.1 contains mode detection and snapshot checkpoint."""

    @classmethod
    def setUpClass(cls):
        cls.content = SKILL_MD_PATH.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()

    def test_step11_titled_capture_intent_and_detect_mode(self):
        """Step 1.1 should be titled Capture Intent and Detect Mode."""
        found = any(
            "Step 1.1" in line and "Capture Intent" in line and "Detect Mode" in line
            for line in self.lines
        )
        self.assertTrue(found, "Step 1.1 should be titled Capture Intent and Detect Mode")

    def test_mode_detection_is_mandatory(self):
        """SKILL.md must contain MODE DETECTION MANDATORY section."""
        self.assertIn("MODE DETECTION", self.content)
        idx = self.content.index("MODE DETECTION")
        nearby = self.content[idx:idx+200]
        self.assertIn("MANDATORY", nearby)

    def test_config_json_creation_documented(self):
        """config.json creation must be documented as NOT optional."""
        self.assertIn("config.json", self.content)
        idx = self.content.index("config.json")
        nearby = self.content[max(0,idx-100):idx+200]
        self.assertTrue(
            "NOT optional" in nearby or "MANDATORY" in nearby,
            "config.json creation must be marked as NOT optional or MANDATORY"
        )

    def test_snapshot_is_hard_gate(self):
        """Snapshot verification must be documented as a hard gate."""
        content_lower = self.content.lower()
        self.assertIn("snapshot", content_lower)
        self.assertIn("hard gate", content_lower)

    def test_config_json_example_format(self):
        """config.json example must include mode, base_skill_path, skill_name, iteration."""
        self.assertIn('"mode"', self.content)
        self.assertIn('"base_skill_path"', self.content)
        self.assertIn('"skill_name"', self.content)
        self.assertIn('"iteration"', self.content)

    def test_mode_determination_rules(self):
        """Mode determination rules must be documented."""
        self.assertIn('"new"', self.content)
        self.assertIn('"improvement"', self.content)

    def test_snapshot_copy_entire_directory(self):
        """Snapshot must copy entire skill directory."""
        self.assertIn("skill-snapshot", self.content)


if __name__ == "__main__":
    unittest.main()
