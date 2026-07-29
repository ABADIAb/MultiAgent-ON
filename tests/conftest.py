"""Root conftest.py — shared pytest configuration.

Registers custom markers so pytest doesn't emit PytestUnknownMarkWarning.
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register project-wide pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require real infrastructure (VPN, API keys). "
        "Run with: uv run pytest -m integration",
    )
