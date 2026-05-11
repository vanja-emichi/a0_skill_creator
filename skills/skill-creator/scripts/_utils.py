#!/usr/bin/env python3
"""Shared utilities for benchmark and report scripts."""

import json
import re
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    """Read a JSON file, returning None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_config(path: Path) -> dict | None:
    """Read a config.json file and return dict with mode, base_skill_path, skill_name, iteration.

    Args:
        path: Path to config.json file.

    Returns:
        Dict with mode, base_skill_path, skill_name, iteration keys, or None if missing/invalid.
    """
    data = read_json(path)
    if data is None or not isinstance(data, dict):
        return None
    return data


def extract_num(prefix: str, path: Path) -> int:
    """Extract a number from a directory name like 'eval-3' or 'iteration-2'.

    Args:
        prefix: The prefix before the number (e.g. 'eval-', 'iteration-').
        path: The Path whose .name is parsed.

    Returns:
        The extracted integer, or 0 if parsing fails.
    """
    name = path.name
    if name.startswith(prefix):
        try:
            return int(name.split("-", 1)[1])
        except (ValueError, IndexError):
            pass
    return 0


def extract_eval_num(path: Path) -> int:
    """Extract eval number from a directory name like 'eval-3'."""
    return extract_num("eval-", path)


def extract_iteration_num(path: Path) -> int:
    """Extract iteration number from a directory name like 'iteration-2'."""
    return extract_num("iteration-", path)


def sanitize_for_prompt(text: str) -> str:
    """Strip HTML comments and truncate skill content for safe prompt embedding."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text


def sanitize_query(query: str, max_len: int = 200) -> str:
    """Truncate and strip newlines from a user query before embedding."""
    query = query.replace("\n", " ").replace("\r", " ")
    if len(query) > max_len:
        query = query[:max_len]
    return query.strip()


def escape_markdown_table(text: str) -> str:
    """Escape special markdown characters in content embedded in tables."""
    text = text.replace("|", "\\|")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("*", "\\*")
    return text
