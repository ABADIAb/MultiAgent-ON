---
name: pytest-expert
description: "Trigger: pytest, python testing, test python code, python tests. Enforce strict TDD, fixtures, and mock patterns for LangGraph and RESTConf in Python."
license: Apache-2.0
metadata:
  author: felipe-abadia
  version: "1.0"
---

## Activation Contract

Create a Python test using Pytest when:
- The `Strict TDD Mode` is active.
- New LangGraph nodes, states, or mathematical tools (e.g., QoT equations) are being implemented.
- Mocking RESTConf NBI responses for Topology extraction.

## Hard Rules

- **Use Pytest:** All tests must be written for `pytest`. Never use `unittest.TestCase`.
- **Fixtures:** Define test topologies, states, and repetitive mock configurations as Pytest fixtures in `conftest.py` or locally.
- **Mocking:** Use `pytest-mock` (mocker) or `unittest.mock` rigorously for the RESTConf API calls and complex LangGraph sub-graphs to ensure tests are isolated and offline.
- **Physical Exactness:** Tests for the GN Model physics equations must include floating-point tolerances (e.g., `pytest.approx()`) for validating SNR and Power calculations against known-good baselines.

## Execution Steps

1. Identify the module to test (e.g., `src/agents/qot_tool.py`).
2. Create or open the corresponding test file in the `tests/` folder (e.g., `tests/agents/test_qot_tool.py`).
3. Write isolated unit tests for the functions, using `pytest.approx` for math.
4. If testing the LangGraph Orchestrator, mock the sub-agents and LLM API calls completely to verify the State transitions.
5. Run tests locally and iterate if any assertions fail.

## Output Contract

Return:
- The path to the created or modified test file.
- A brief summary of what was mocked and what behavior was validated.
