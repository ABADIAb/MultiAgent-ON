"""Tests for the PDDL CFG syntax validator.

Validates that the regex-based structural validator correctly identifies
well-formed PDDL problem strings and rejects malformed ones.

Strict TDD: these tests are written BEFORE the implementation.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def valid_pddl() -> str:
    """A well-formed simplified PDDL problem string for optical routing."""
    return (
        "(define (problem optical-route-001)\n"
        "  (:domain optical-network)\n"
        "  (:objects\n"
        "    Milano-A Milano-B Milano-C Milano-D - node\n"
        "  )\n"
        "  (:init\n"
        "    (connected Milano-A Milano-B)\n"
        "    (connected Milano-B Milano-C)\n"
        "    (connected Milano-C Milano-D)\n"
        "  )\n"
        "  (:goal\n"
        "    (and\n"
        "      (route Milano-A Milano-D)\n"
        "      (min-gsnr 15)\n"
        "    )\n"
        "  )\n"
        ")"
    )


@pytest.fixture()
def minimal_valid_pddl() -> str:
    """Minimal PDDL problem with all required sections but sparse content."""
    return (
        "(define (problem minimal-test)\n"
        "  (:domain optical-network)\n"
        "  (:objects node-A - node)\n"
        "  (:init (connected node-A node-A))\n"
        "  (:goal (route node-A node-A))\n"
        ")"
    )


# ---------------------------------------------------------------------------
# Tests: validate_pddl_syntax
# ---------------------------------------------------------------------------


class TestValidatePddlSyntax:
    """Test the main PDDL structural validation function."""

    def test_valid_pddl_passes(self, valid_pddl: str):
        from src.core.pddl_validator import validate_pddl_syntax

        is_valid, errors = validate_pddl_syntax(valid_pddl)
        assert is_valid is True
        assert errors == []

    def test_minimal_valid_pddl_passes(self, minimal_valid_pddl: str):
        from src.core.pddl_validator import validate_pddl_syntax

        is_valid, errors = validate_pddl_syntax(minimal_valid_pddl)
        assert is_valid is True
        assert errors == []

    def test_empty_string_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        is_valid, errors = validate_pddl_syntax("")
        assert is_valid is False
        assert len(errors) > 0

    def test_missing_closing_parenthesis_fails(self, valid_pddl: str):
        from src.core.pddl_validator import validate_pddl_syntax

        # Remove the last closing paren
        broken = valid_pddl.rstrip(")\n ")[:-1]
        is_valid, errors = validate_pddl_syntax(broken)
        assert is_valid is False
        assert any("parenthes" in e.lower() for e in errors)

    def test_extra_closing_parenthesis_fails(self, valid_pddl: str):
        from src.core.pddl_validator import validate_pddl_syntax

        broken = valid_pddl + ")"
        is_valid, errors = validate_pddl_syntax(broken)
        assert is_valid is False
        assert any("parenthes" in e.lower() for e in errors)

    def test_missing_define_keyword_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = "(problem test (:domain d) (:objects x) (:init (a)) (:goal (b)))"
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("define" in e.lower() for e in errors)

    def test_missing_problem_keyword_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = "(define (:domain d) (:objects x) (:init (a)) (:goal (b)))"
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("problem" in e.lower() for e in errors)

    def test_missing_domain_section_fails(self, valid_pddl: str):
        from src.core.pddl_validator import validate_pddl_syntax

        broken = valid_pddl.replace("(:domain optical-network)\n", "")
        is_valid, errors = validate_pddl_syntax(broken)
        assert is_valid is False
        assert any(":domain" in e.lower() for e in errors)

    def test_missing_goal_section_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem no-goal)\n"
            "  (:domain optical-network)\n"
            "  (:objects x - node)\n"
            "  (:init (connected x x))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any(":goal" in e.lower() for e in errors)

    def test_missing_objects_section_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem no-objects)\n"
            "  (:domain optical-network)\n"
            "  (:init (connected x x))\n"
            "  (:goal (route x x))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any(":objects" in e.lower() for e in errors)

    def test_missing_init_section_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem no-init)\n"
            "  (:domain optical-network)\n"
            "  (:objects x - node)\n"
            "  (:goal (route x x))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any(":init" in e.lower() for e in errors)

    def test_extra_unknown_sections_still_valid(self):
        """Unknown sections are permissive — the validator only checks required ones."""
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem extra-sections)\n"
            "  (:domain optical-network)\n"
            "  (:objects x - node)\n"
            "  (:init (connected x x))\n"
            "  (:constraints (preference p1 (sometime (at x))))\n"
            "  (:goal (route x x))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is True
        assert errors == []

    def test_deeply_nested_balanced_parens_valid(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem nested)\n"
            "  (:domain optical-network)\n"
            "  (:objects x - node)\n"
            "  (:init (and (connected x x) (active x)))\n"
            "  (:goal (and (or (route x x) (route x x)) (min-gsnr 10)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is True

    def test_whitespace_only_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        is_valid, errors = validate_pddl_syntax("   \n\t  ")
        assert is_valid is False

    def test_random_text_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        is_valid, errors = validate_pddl_syntax("Route from A to B please")
        assert is_valid is False


# ---------------------------------------------------------------------------
# Tests: extract_pddl_sections
# ---------------------------------------------------------------------------


class TestExtractPddlSections:
    """Test the PDDL section extraction helper."""

    def test_extracts_all_required_sections(self, valid_pddl: str):
        from src.core.pddl_validator import extract_pddl_sections

        sections = extract_pddl_sections(valid_pddl)
        assert "domain" in sections
        assert "objects" in sections
        assert "init" in sections
        assert "goal" in sections

    def test_domain_content_correct(self, valid_pddl: str):
        from src.core.pddl_validator import extract_pddl_sections

        sections = extract_pddl_sections(valid_pddl)
        assert "optical-network" in sections["domain"]

    def test_goal_content_correct(self, valid_pddl: str):
        from src.core.pddl_validator import extract_pddl_sections

        sections = extract_pddl_sections(valid_pddl)
        assert "route" in sections["goal"].lower() or "Milano" in sections["goal"]

    def test_empty_string_returns_empty_dict(self):
        from src.core.pddl_validator import extract_pddl_sections

        sections = extract_pddl_sections("")
        assert sections == {}

    def test_problem_name_extracted(self, valid_pddl: str):
        from src.core.pddl_validator import extract_pddl_sections

        sections = extract_pddl_sections(valid_pddl)
        assert "problem_name" in sections
        assert sections["problem_name"] == "optical-route-001"


# ---------------------------------------------------------------------------
# Tests: CFG Grammar & AST Parsing (parse_pddl_ast & predicate validation)
# ---------------------------------------------------------------------------


class TestPddlCfgAstGrammar:
    """Test full CFG grammar rules and AST extraction."""

    def test_avoid_node_goal_valid(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem avoid-node-test)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich Hamburg - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (avoid-node Hamburg) (min-gsnr 15.5)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is True
        assert errors == []

    def test_avoid_nodes_multiple_valid(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem avoid-nodes-test)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich Hamburg Leipzig - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (avoid-nodes Hamburg Leipzig)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is True
        assert errors == []

    def test_route_missing_destination_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem bad-route)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("requires exactly 2 arguments" in e for e in errors)

    def test_max_hops_non_integer_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem bad-hops)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (max-hops two)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("must be an integer" in e for e in errors)

    def test_min_gsnr_non_numeric_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem bad-gsnr)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (min-gsnr high)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("must be a number" in e for e in errors)

    def test_bandwidth_integer_passes(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem bandwidth-test)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (bandwidth 100)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is True
        assert errors == []

    def test_bandwidth_non_integer_fails(self):
        from src.core.pddl_validator import validate_pddl_syntax

        pddl = (
            "(define (problem bad-bandwidth)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Munich - node)\n"
            "  (:init (connected Berlin Munich))\n"
            "  (:goal (and (route Berlin Munich) (bandwidth high)))\n"
            ")"
        )
        is_valid, errors = validate_pddl_syntax(pddl)
        assert is_valid is False
        assert any("must be an integer" in e for e in errors)

    def test_parse_pddl_ast_success(self, valid_pddl: str):
        from src.core.pddl_validator import parse_pddl_ast

        ast, errors = parse_pddl_ast(valid_pddl)
        assert errors == []
        assert isinstance(ast, list)
        assert len(ast) > 0
        assert ast[0][0] == "define"

