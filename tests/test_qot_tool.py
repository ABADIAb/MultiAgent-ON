"""Tests for the QoT LangChain tool wrapper.

Written FIRST (RED phase) per Strict TDD Mode.
Tests the @tool decorator metadata and the integration between
the tool interface and the underlying qot_calculator.
"""

from __future__ import annotations

import pytest

from src.core.models import Amplifier, FiberLink


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def sample_path_input() -> list[dict]:
    """Raw dict input representing a valid path for the tool."""
    return [
        {
            "link_id": 0,
            "src_node_id": 0,
            "dst_node_id": 1,
            "length_km": 80,
            "port_loss_dB": 0.0,
            "amplifiers": [
                {
                    "position_km": 40,
                    "gain_dB": 10.0,
                    "amp_type": "ila",
                },
                {
                    "position_km": 80,
                    "gain_dB": 10.0,
                    "amp_type": "preamp",
                },
            ],
        },
    ]


@pytest.fixture()
def sample_fiber_links() -> list[FiberLink]:
    """Pre-built FiberLink objects for the same path."""
    return [
        FiberLink(
            link_id=0,
            src_node_id=0,
            dst_node_id=1,
            length_km=80,
            port_loss_dB=0.0,
            amplifiers=[
                Amplifier(position_km=40, gain_dB=10.0, amp_type="ila"),
                Amplifier(position_km=80, gain_dB=10.0, amp_type="preamp"),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Tool metadata
# ---------------------------------------------------------------------------
class TestToolMetadata:
    """Validate that the tool is properly decorated for LangGraph discovery."""

    def test_tool_has_name(self) -> None:
        from src.tools.qot_tool import qot_check

        assert qot_check.name == "qot_check"

    def test_tool_has_description(self) -> None:
        from src.tools.qot_tool import qot_check

        assert qot_check.description
        assert "QoT" in qot_check.description or "quality" in qot_check.description.lower()


# ---------------------------------------------------------------------------
# Tool invocation
# ---------------------------------------------------------------------------
class TestToolInvocation:
    """Validate the tool returns correct results."""

    def test_returns_dict_with_required_keys(
        self, sample_path_input: list[dict]
    ) -> None:
        from src.tools.qot_tool import qot_check

        result = qot_check.invoke(
            {"path": sample_path_input, "bitrate_gbps": 100}
        )
        assert isinstance(result, dict)
        assert "feasible" in result
        assert "snr_dB" in result
        assert "power_dBm" in result

    def test_feasible_path_returns_true(
        self, sample_path_input: list[dict]
    ) -> None:
        from src.tools.qot_tool import qot_check

        result = qot_check.invoke(
            {"path": sample_path_input, "bitrate_gbps": 100}
        )
        assert result["feasible"] is True

    def test_snr_matches_calculator(
        self, sample_path_input: list[dict]
    ) -> None:
        """Tool output should match the raw calculator output."""
        from src.tools.qot_tool import qot_check

        result = qot_check.invoke(
            {"path": sample_path_input, "bitrate_gbps": 100}
        )
        assert result["snr_dB"] == pytest.approx(19.9562, abs=0.1)
        assert result["power_dBm"] == pytest.approx(-16.0, abs=0.1)

    def test_empty_path_returns_error(self) -> None:
        from src.tools.qot_tool import qot_check

        result = qot_check.invoke({"path": [], "bitrate_gbps": 100})
        assert isinstance(result, dict)
        assert "error" in result

    def test_default_bitrate_is_100g(
        self, sample_path_input: list[dict]
    ) -> None:
        from src.tools.qot_tool import qot_check

        result = qot_check.invoke({"path": sample_path_input})
        assert isinstance(result, dict)
        assert "feasible" in result
