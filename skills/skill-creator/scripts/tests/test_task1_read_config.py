#!/usr/bin/env python3
"""Tests for Task 1: read_config() helper in _utils.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestReadConfig(unittest.TestCase):
    """Test read_config() reads config.json and returns expected dict."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpdir_path = Path(self.tmpdir)

    def _write_config(self, data: dict):
        config_path = self.tmpdir_path / "config.json"
        config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return config_path

    def test_read_config_returns_dict_with_all_fields(self):
        """read_config should return dict with mode, base_skill_path, skill_name, iteration."""
        from _utils import read_config

        config_data = {
            "mode": "new",
            "base_skill_path": "/path/to/skill/SKILL.md",
            "skill_name": "my-skill",
            "iteration": 1,
        }
        config_path = self._write_config(config_data)
        result = read_config(config_path)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["mode"], "new")
        self.assertEqual(result["base_skill_path"], "/path/to/skill/SKILL.md")
        self.assertEqual(result["skill_name"], "my-skill")
        self.assertEqual(result["iteration"], 1)

    def test_read_config_improvement_mode(self):
        """read_config should handle improvement mode correctly."""
        from _utils import read_config

        config_data = {
            "mode": "improvement",
            "base_skill_path": "/path/to/existing/SKILL.md",
            "skill_name": "existing-skill",
            "iteration": 3,
        }
        config_path = self._write_config(config_data)
        result = read_config(config_path)

        self.assertEqual(result["mode"], "improvement")
        self.assertEqual(result["iteration"], 3)

    def test_read_config_missing_file_returns_none(self):
        """read_config should return None for missing file."""
        from _utils import read_config

        result = read_config(self.tmpdir_path / "nonexistent.json")
        self.assertIsNone(result)

    def test_read_config_invalid_json_returns_none(self):
        """read_config should return None for invalid JSON."""
        from _utils import read_config

        bad_path = self.tmpdir_path / "bad.json"
        bad_path.write_text("not valid json {{{", encoding="utf-8")
        result = read_config(bad_path)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
