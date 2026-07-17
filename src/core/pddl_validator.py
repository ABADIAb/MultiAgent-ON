"""PDDL CFG syntax validator for the Neurosymbolic Intent Pipeline.

Provides lightweight structural validation of simplified PDDL problem
strings using regex-based checks. This is NOT a full PDDL 3.1 parser —
it catches the most common LLM hallucination patterns:
  - Unbalanced parentheses
  - Missing required sections (define, problem, :domain, :objects, :init, :goal)
  - Empty or whitespace-only input

Design choice: permissive on unknown sections (e.g., :constraints, :metric)
to allow domain-specific extensions without breaking validation.
"""

from __future__ import annotations

import re

# Required PDDL sections for our simplified optical network domain
REQUIRED_SECTIONS = frozenset({"domain", "objects", "init", "goal"})


def validate_pddl_syntax(pddl_string: str) -> tuple[bool, list[str]]:
    """Validate structural syntax of a simplified PDDL problem string.

    Checks:
        1. Non-empty input
        2. Balanced parentheses
        3. ``(define (problem <name>) ...)`` wrapper
        4. All required sections present: :domain, :objects, :init, :goal

    Args:
        pddl_string: The PDDL string to validate.

    Returns:
        A tuple of (is_valid, list_of_error_messages).
        If valid, errors list is empty.
    """
    errors: list[str] = []

    # 1. Non-empty
    stripped = pddl_string.strip()
    if not stripped:
        errors.append("PDDL string is empty or whitespace-only.")
        return False, errors

    # 2. Balanced parentheses
    depth = 0
    for i, ch in enumerate(stripped):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            errors.append(
                f"Unbalanced parentheses: extra closing ')' at position {i}."
            )
            return False, errors
    if depth != 0:
        errors.append(
            f"Unbalanced parentheses: {depth} unclosed '(' remaining."
        )

    # 3. (define (problem <name>) ...) wrapper
    if not re.search(r"\(\s*define\b", stripped):
        errors.append("Missing 'define' keyword: expected '(define ...)'.")

    if not re.search(r"\(\s*problem\s+\S+", stripped):
        errors.append("Missing 'problem' declaration: expected '(problem <name>)'.")

    # 4. Required sections
    for section in sorted(REQUIRED_SECTIONS):
        pattern = rf"\(\s*:{section}\b"
        if not re.search(pattern, stripped):
            errors.append(f"Missing required section ':{section}'.")

    return (len(errors) == 0), errors


def extract_pddl_sections(pddl_string: str) -> dict[str, str]:
    """Extract named sections from a PDDL problem string.

    Parses the PDDL string into a dictionary keyed by section name
    (without the colon prefix). Also extracts ``problem_name``.

    Args:
        pddl_string: The PDDL string to parse.

    Returns:
        A dict mapping section names to their content strings.
        Returns empty dict for empty or unparseable input.
    """
    stripped = pddl_string.strip()
    if not stripped:
        return {}

    result: dict[str, str] = {}

    # Extract problem name
    m = re.search(r"\(\s*problem\s+(\S+)", stripped)
    if m:
        # Clean trailing paren if the name ends with one
        name = m.group(1).rstrip(")")
        result["problem_name"] = name

    # Extract sections like (:domain ...), (:objects ...), etc.
    # Strategy: find each (:<section_name> and extract until the matching
    # closing paren by counting depth.
    section_starts = list(re.finditer(r"\(\s*:(\w+)\b", stripped))

    for match in section_starts:
        section_name = match.group(1)
        start = match.start()

        # Walk from start, counting parens to find the matching close
        depth = 0
        end = start
        for i in range(start, len(stripped)):
            if stripped[i] == "(":
                depth += 1
            elif stripped[i] == ")":
                depth -= 1
            if depth == 0:
                end = i + 1
                break

        # Content is everything between the section keyword and closing paren
        content = stripped[start:end]
        result[section_name] = content

    return result
