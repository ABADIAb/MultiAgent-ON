"""PDDL CFG syntax and structural validator for the Neurosymbolic Intent Pipeline.

Provides rigorous structural and Context-Free Grammar (CFG) validation of
simplified PDDL problem strings using S-expression tokenization and AST parsing.
Validates:
  - Parenthesis balance and S-expression nesting
  - Problem declaration: ``(define (problem <name>) ...)``
  - Mandatory sections: ``:domain``, ``:objects``, ``:init``, ``:goal``
  - Grammar production rules for routing predicates (arity and type constraints):
    - ``(route <src> <dst>)`` and routing aliases
    - ``(avoid-node <node>)`` and ``(avoid-nodes <node>...)``
    - ``(avoid-link <link_id>)`` or ``(avoid-link <src> <dst>)``
    - ``(max-hops <int>)``
    - ``(min-gsnr <float|int>)``

Permissive on optional sections (e.g., ``:constraints``, ``:metric``) and
user-defined initial topology predicates to preserve domain extensibility.
"""

from __future__ import annotations

import re
from typing import Any

REQUIRED_SECTIONS = frozenset({"domain", "objects", "init", "goal"})

# Recognized routing predicates and their arities/validators
_ROUTING_PREDICATES = frozenset({
    "route", "routed", "path", "route-traffic", "service", "connect",
})
_AVOID_NODE_PREDICATES = frozenset({"avoid-node", "avoid-nodes", "avoid"})
_AVOID_LINK_PREDICATES = frozenset({"avoid-link", "avoid-links"})
_MAX_HOPS_PREDICATES = frozenset({"max-hops", "max_hops", "hops"})
_MIN_GSNR_PREDICATES = frozenset({
    "min-gsnr", "min-snr", "target-snr", "min_gsnr", "target_snr",
})


# ---------------------------------------------------------------------------
# S-Expression Lexer and Parser (CFG AST Builder)
# ---------------------------------------------------------------------------


def _tokenize(pddl_string: str) -> tuple[list[str], list[str]]:
    """Tokenize a PDDL string into S-expression tokens.

    Handles comments (starting with ';') and parentheses.

    Returns:
        A tuple of (tokens, errors).
    """
    errors: list[str] = []
    # Strip comments
    lines = []
    for line in pddl_string.splitlines():
        comment_idx = line.find(";")
        if comment_idx != -1:
            line = line[:comment_idx]
        lines.append(line)
    clean_text = "\n".join(lines).strip()

    if not clean_text:
        errors.append("PDDL string is empty or whitespace-only.")
        return [], errors

    # Check balanced parentheses depth and positions
    depth = 0
    for i, ch in enumerate(clean_text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            errors.append(f"Unbalanced parentheses: extra closing ')' at position {i}.")
            return [], errors

    if depth != 0:
        errors.append(f"Unbalanced parentheses: {depth} unclosed '(' remaining.")
        return [], errors

    # Tokenize parentheses and whitespace-delimited words
    raw_tokens = re.findall(r"\(|\)|[^\s()]+", clean_text)
    return raw_tokens, errors


def _parse_s_expressions(tokens: list[str]) -> list[Any]:
    """Parse tokens into nested S-expression lists."""
    stack: list[list[Any]] = [[]]

    for token in tokens:
        if token == "(":
            new_list: list[Any] = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif token == ")":
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(token)

    return stack[0]


def parse_pddl_ast(pddl_string: str) -> tuple[list[Any] | None, list[str]]:
    """Parse a PDDL problem string into a structured S-expression AST.

    Args:
        pddl_string: Raw PDDL string.

    Returns:
        A tuple of (ast_tree, error_list).
    """
    tokens, errors = _tokenize(pddl_string)
    if errors:
        return None, errors

    try:
        parsed = _parse_s_expressions(tokens)
        if not parsed:
            return None, ["Empty S-expression tree."]
        return parsed, []
    except Exception as exc:
        return None, [f"S-expression parsing failed: {exc}"]


# ---------------------------------------------------------------------------
# Grammar Rule Validators (CFG)
# ---------------------------------------------------------------------------


def _validate_numeric(val: str, allow_float: bool = True) -> bool:
    """Check if a string token is a valid numeric constant."""
    if not isinstance(val, str):
        return False
    if allow_float:
        return bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", val))
    return bool(re.fullmatch(r"[-+]?\d+", val))


def _validate_goal_predicate(pred: Any, errors: list[str]) -> None:
    """Validate a single predicate AST node in the :goal section."""
    if not isinstance(pred, list) or len(pred) == 0:
        errors.append(f"Malformed goal expression: expected predicate list, got {pred!r}.")
        return

    # Handle logical connectives (and, or, not)
    name = str(pred[0]).lower()
    if name in {"and", "or"}:
        for sub_expr in pred[1:]:
            _validate_goal_predicate(sub_expr, errors)
        return
    if name == "not":
        if len(pred) != 2:
            errors.append(f"Logical 'not' in goal expects exactly 1 sub-expression, got {len(pred)-1}.")
        else:
            _validate_goal_predicate(pred[1], errors)
        return

    # Check known domain predicate schemas
    args = pred[1:]
    if name in _ROUTING_PREDICATES:
        if len(args) != 2:
            errors.append(f"Predicate '({name})' requires exactly 2 arguments (source destination), got {len(args)}.")
    elif name in _AVOID_NODE_PREDICATES:
        if len(args) < 1:
            errors.append(f"Predicate '({name})' requires at least 1 node argument, got 0.")
    elif name in _AVOID_LINK_PREDICATES:
        if len(args) not in {1, 2}:
            errors.append(f"Predicate '({name})' requires 1 link ID or 2 node endpoints, got {len(args)}.")
    elif name in _MAX_HOPS_PREDICATES:
        if len(args) != 1:
            errors.append(f"Predicate '({name})' requires exactly 1 integer argument, got {len(args)}.")
        elif not _validate_numeric(str(args[0]), allow_float=False):
            errors.append(f"Predicate '({name})' argument must be an integer, got {args[0]!r}.")
    elif name in _MIN_GSNR_PREDICATES:
        if len(args) != 1:
            errors.append(f"Predicate '({name})' requires exactly 1 numeric argument, got {len(args)}.")
        elif not _validate_numeric(str(args[0]), allow_float=True):
            errors.append(f"Predicate '({name})' argument must be a number, got {args[0]!r}.")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_pddl_syntax(pddl_string: str) -> tuple[bool, list[str]]:
    """Validate structural and CFG syntax of a simplified PDDL problem string.

    Checks:
        1. Non-empty input and balanced parentheses
        2. ``(define (problem <name>) ...)`` outer problem wrapper
        3. Mandatory sections: ``:domain``, ``:objects``, ``:init``, ``:goal``
        4. AST grammar rules for goal predicates and numeric constraints

    Args:
        pddl_string: The PDDL string to validate.

    Returns:
        A tuple of (is_valid, list_of_error_messages).
        If valid, errors list is empty.
    """
    errors: list[str] = []
    stripped = pddl_string.strip()
    if not stripped:
        errors.append("PDDL string is empty or whitespace-only.")
        return False, errors

    # Check define and problem keywords early for clear error diagnostics
    if not re.search(r"\(\s*define\b", stripped):
        errors.append("Missing 'define' keyword: expected '(define ...)'.")
    if not re.search(r"\(\s*problem\s+\S+", stripped):
        errors.append("Missing 'problem' declaration: expected '(problem <name>)'.")

    # Check required section keywords
    for section in sorted(REQUIRED_SECTIONS):
        pattern = rf"\(\s*:{section}\b"
        if not re.search(pattern, stripped):
            errors.append(f"Missing required section ':{section}'.")

    # If any top-level keyword check failed, return early
    if errors:
        return False, errors

    # Parse into AST tree
    ast_tree, ast_errors = parse_pddl_ast(stripped)
    if ast_errors or not ast_tree:
        errors.extend(ast_errors)
        return False, errors

    # Validate AST structure
    top_expr = ast_tree[0] if isinstance(ast_tree[0], list) else ast_tree
    if not isinstance(top_expr, list) or len(top_expr) < 2 or str(top_expr[0]).lower() != "define":
        errors.append("Root expression must be '(define ...)'")
        return False, errors

    # Extract sections from AST
    sections_found: dict[str, Any] = {}
    for item in top_expr[1:]:
        if isinstance(item, list) and len(item) > 0:
            header = str(item[0])
            if header.startswith(":"):
                sections_found[header[1:].lower()] = item
            elif header.lower() == "problem":
                sections_found["problem"] = item

    # Check goal section grammar in AST
    goal_section = sections_found.get("goal")
    if goal_section and len(goal_section) > 1:
        goal_content = goal_section[1]
        _validate_goal_predicate(goal_content, errors)

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
        name = m.group(1).rstrip(")")
        result["problem_name"] = name

    # Extract sections like (:domain ...), (:objects ...), etc.
    section_starts = list(re.finditer(r"\(\s*:(\w+)\b", stripped))

    for match in section_starts:
        section_name = match.group(1)
        start = match.start()

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

        content = stripped[start:end]
        result[section_name] = content

    return result
