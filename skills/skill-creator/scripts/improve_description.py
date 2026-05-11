#!/usr/bin/env python3
"""Parse and validate improved trigger_patterns and description from agent output."""

import re
from typing import Any


# Maximum allowed description length (characters)
MAX_DESCRIPTION_LENGTH = 1024


def extract_tag_content(text: str, tag: str) -> str | None:
    """Extract content between XML-style tags.

    Args:
        text: Full text containing tagged content.
        tag: Tag name (e.g., "new_description").

    Returns:
        Extracted content stripped of whitespace, or None if tag not found.
    """
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def parse_triggers(text: str) -> list[str]:
    """Parse trigger patterns from agent output.

    Handles formats:
    - Bullet list: "- trigger one\n- trigger two"
    - Numbered list: "1. trigger one\n2. trigger two"
    - Plain lines (one per trigger)

    Args:
        text: Raw trigger patterns text from <new_triggers> tags.

    Returns:
        List of trigger pattern strings.
    """
    triggers = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Strip bullet or number prefixes
        line = re.sub(r"^[-*•]\s+", "", line)
        line = re.sub(r"^\d+[.)]\s+", "", line)
        if line:
            triggers.append(line)
    return triggers


def extract_improvement(output: str) -> dict[str, Any]:
    """Extract and validate improved description and triggers from agent output.

    Args:
        output: Raw agent output text containing <new_description> and <new_triggers> tags.

    Returns:
        Dict with:
            - description: str or None
            - trigger_patterns: list[str]
            - needs_shortening: bool
            - errors: list[str]
    """
    result = {
        "description": None,
        "trigger_patterns": [],
        "needs_shortening": False,
        "errors": [],
    }

    # Extract description
    desc = extract_tag_content(output, "new_description")
    if desc is None:
        result["errors"].append("Missing <new_description> tags in agent output")
    else:
        result["description"] = desc
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            result["needs_shortening"] = True

    # Extract triggers
    triggers_text = extract_tag_content(output, "new_triggers")
    if triggers_text is None:
        result["errors"].append("Missing <new_triggers> tags in agent output")
    else:
        triggers = parse_triggers(triggers_text)
        if not triggers:
            result["errors"].append("No trigger patterns found in <new_triggers> content")
        else:
            result["trigger_patterns"] = triggers

    return result


def validate_triggers(triggers: list[str], min_count: int = 3, max_count: int = 20) -> list[str]:
    """Validate trigger patterns for quality.

    Args:
        triggers: List of trigger pattern strings.
        min_count: Minimum number of triggers expected.
        max_count: Maximum number of triggers allowed.

    Returns:
        List of validation warning strings (empty if all good).
    """
    warnings = []

    if len(triggers) < min_count:
        warnings.append(f"Only {len(triggers)} triggers (minimum {min_count} recommended)")

    if len(triggers) > max_count:
        warnings.append(f"{len(triggers)} triggers exceeds maximum of {max_count}")

    seen = set()
    for t in triggers:
        t_lower = t.lower().strip()
        if t_lower in seen:
            warnings.append(f"Duplicate trigger: '{t}'")
        seen.add(t_lower)

        if len(t) > 100:
            warnings.append(f"Trigger too long ({len(t)} chars): '{t[:50]}...'")

        if t.lower() == t and any(c.isalpha() for c in t) and len(t.split()) < 2:
            warnings.append(f"Single-word trigger may be too broad: '{t}'")

    return warnings


def validate_description(description: str) -> list[str]:
    """Validate a skill description.

    Args:
        description: Description text.

    Returns:
        List of validation warning strings (empty if all good).
    """
    warnings = []

    if not description:
        warnings.append("Description is empty")
        return warnings

    if len(description) > MAX_DESCRIPTION_LENGTH:
        warnings.append(
            f"Description is {len(description)} chars (max {MAX_DESCRIPTION_LENGTH})"
        )

    if len(description) < 50:
        warnings.append("Description may be too short to be descriptive")

    if description.count("\n") > 5:
        warnings.append("Description has many newlines — consider a more compact format")

    return warnings


def format_shortening_request(description: str) -> str:
    """Build a follow-up prompt asking the agent to shorten a long description.

    Args:
        description: Description exceeding MAX_DESCRIPTION_LENGTH.

    Returns:
        Prompt string for the shortening request.
    """
    excess = len(description) - MAX_DESCRIPTION_LENGTH
    return (
        f"The description you provided is {len(description)} characters, "
        f"which exceeds the {MAX_DESCRIPTION_LENGTH}-character limit by {excess} characters. "
        f"Please shorten it while preserving the key trigger conditions and use cases.\n\n"
        f"Return the shortened description in <new_description> tags."
    )
