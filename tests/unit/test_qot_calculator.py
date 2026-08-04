"""Tests for the QoT calculator — GN model physics engine.

Written FIRST (RED phase) per Strict TDD Mode.
All reference values computed from the exact C++ constants
(Network.h, OaLoc.h) using hand-verified GN model calculations.
"""

from __future__ import annotations

import math

import pytest

from src.core.constants import (
    AMPLIFIER,
    CHANNEL,
    FIBER,
    NODE,
    THRESHOLD,
    AmplifierConstants,
    ChannelConstants,
    FiberConstants,
    NodeConstants,
    ThresholdConstants,
)
from src.core.models import Amplifier, FiberLink, QoTResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def fiber_constants() -> FiberConstants:
    return FIBER


@pytest.fixture()
def channel_constants() -> ChannelConstants:
    return CHANNEL


@pytest.fixture()
def node_constants() -> NodeConstants:
    return NODE


@pytest.fixture()
def amp_constants() -> AmplifierConstants:
    return AMPLIFIER


@pytest.fixture()
def single_link_ila_preamp() -> list[FiberLink]:
    """80 km link with ILA at 40km (10dB) and preamp at 80km (10dB).

    Expected results (hand-computed):
        SNR = 19.9562 dB, Rx power = -16.00 dBm
    """
    return [
        FiberLink(
            link_id=0,
            src_node_id=0,
            dst_node_id=1,
            length_km=80,
            port_loss_dB=0.0,
            amplifiers=[
                Amplifier(
                    position_km=40,
                    gain_dB=10.0,
                    amp_type="ila",
                ),
                Amplifier(
                    position_km=80,
                    gain_dB=10.0,
                    amp_type="preamp",
                ),
            ],
        ),
    ]


@pytest.fixture()
def single_link_ila_no_preamp() -> list[FiberLink]:
    """80 km link with ILA at 40km (20dB), no preamp.

    Expected results (hand-computed):
        SNR = 22.9485 dB, Rx power = -15.00 dBm
    """
    return [
        FiberLink(
            link_id=0,
            src_node_id=0,
            dst_node_id=1,
            length_km=80,
            port_loss_dB=0.0,
            amplifiers=[
                Amplifier(
                    position_km=40,
                    gain_dB=20.0,
                    amp_type="ila",
                ),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Constants validation
# ---------------------------------------------------------------------------
class TestConstants:
    """Validate that Python constants match C++ Network.h exactly."""

    def test_alpha_linear_conversion(self, fiber_constants: FiberConstants) -> None:
        """alpha_linear must match C++ formula: att_dB_km / (10*log10(e)) / 1e3."""
        expected = 0.25 / (10.0 * math.log10(math.e)) / 1e3
        assert fiber_constants.alpha_linear == pytest.approx(expected, rel=1e-10)

    def test_n_channels(self, channel_constants: ChannelConstants) -> None:
        assert channel_constants.n_channels == pytest.approx(100.0)

    def test_planck_freq_rs(self, channel_constants: ChannelConstants) -> None:
        expected = 6.62607004e-34 * 193.4e12 * 32e9
        assert channel_constants.planck_freq_rs == pytest.approx(expected, rel=1e-10)

    def test_nsr_trx(self, channel_constants: ChannelConstants) -> None:
        """Transponder NSR = 1/10^(26/10)."""
        nsr = 1.0 / (10 ** (channel_constants.snr_trx_dB / 10.0))
        assert nsr == pytest.approx(2.5118864315e-3, rel=1e-6)

    def test_snr_thresholds(self) -> None:
        assert THRESHOLD.get_snr_threshold(10) == pytest.approx(12.2)
        assert THRESHOLD.get_snr_threshold(100) == pytest.approx(8.6)
        assert THRESHOLD.get_snr_threshold(200) == pytest.approx(15.2)

    def test_unsupported_bitrate_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported bitrate"):
            THRESHOLD.get_snr_threshold(400)


# ---------------------------------------------------------------------------
# Data model validation
# ---------------------------------------------------------------------------
class TestModels:
    """Validate Pydantic data models."""

    def test_amplifier_nf_auto_computed(self) -> None:
        """NF should be auto-computed from gain when not provided."""
        amp = Amplifier(position_km=40, gain_dB=20.0, amp_type="ila")
        assert amp.nf_dB is not None
        # NF for 20dB gain: NF_lin = 2.793 + 117.513/(100-1) = 3.98
        expected_nf_dB = 10.0 * math.log10(3.98)
        assert amp.nf_dB == pytest.approx(expected_nf_dB, rel=1e-4)

    def test_amplifier_nf_explicit(self) -> None:
        """Explicit NF should not be overridden."""
        amp = Amplifier(position_km=40, gain_dB=20.0, nf_dB=5.0, amp_type="ila")
        assert amp.nf_dB == pytest.approx(5.0)

    def test_fiber_link_sorts_amplifiers(self) -> None:
        """Amplifiers should be sorted by position_km."""
        link = FiberLink(
            link_id=0,
            src_node_id=0,
            dst_node_id=1,
            length_km=100,
            amplifiers=[
                Amplifier(position_km=80, gain_dB=10, amp_type="preamp"),
                Amplifier(position_km=40, gain_dB=10, amp_type="ila"),
            ],
        )
        assert link.amplifiers[0].position_km == 40
        assert link.amplifiers[1].position_km == 80

    def test_fiber_link_rejects_bad_amplifier_position(self) -> None:
        """Amplifier beyond link length should raise."""
        with pytest.raises(ValueError, match="exceeds link length"):
            FiberLink(
                link_id=0,
                src_node_id=0,
                dst_node_id=1,
                length_km=50,
                amplifiers=[
                    Amplifier(position_km=60, gain_dB=10, amp_type="ila"),
                ],
            )


# ---------------------------------------------------------------------------
# span_snr validation
# ---------------------------------------------------------------------------
class TestSpanSNR:
    """Validate the span-level SNR computation (maps to C++ spanSNR)."""

    def test_amplified_span_80km(self) -> None:
        """Standard amplified span: 80km fiber, gain=20dB, power_out=1dBm.

        Expected NSR = 2.6194634216e-03 (ASE + NLI).
        """
        from src.core.qot_calculator import span_snr

        nsr, _ = span_snr(
            fiber_length_km=80,
            gain_dB=20.0,
            nf_dB=10.0 * math.log10(3.98),
            power_out_dBm=1.0,
            last_span_no_preamp=False,
        )
        assert nsr == pytest.approx(2.6194634216e-3, rel=1e-4)

    def test_amplified_span_20km(self) -> None:
        """Shorter span: 20km, same amplifier parameters.

        Expected NSR = 1.9207812770e-03.
        """
        from src.core.qot_calculator import span_snr

        nsr, _ = span_snr(
            fiber_length_km=20,
            gain_dB=20.0,
            nf_dB=10.0 * math.log10(3.98),
            power_out_dBm=1.0,
            last_span_no_preamp=False,
        )
        assert nsr == pytest.approx(1.9207812770e-3, rel=1e-4)

    def test_ase_only_no_fiber(self) -> None:
        """Booster with no preceding fiber: NLI = 0, only ASE.

        Expected NSR = 1.2834552682e-03.
        """
        from src.core.qot_calculator import span_snr

        nsr, _ = span_snr(
            fiber_length_km=0,
            gain_dB=20.0,
            nf_dB=10.0 * math.log10(3.98),
            power_out_dBm=1.0,
            last_span_no_preamp=False,
        )
        assert nsr == pytest.approx(1.2834552682e-3, rel=1e-4)

    def test_last_span_no_preamp(self) -> None:
        """Last span without pre-amplifier: NLI only, no ASE.

        80km fiber, input power = 1 dBm.
        Expected NSR = 1.3360081534e-03.
        """
        from src.core.qot_calculator import span_snr

        nsr, _ = span_snr(
            fiber_length_km=80,
            gain_dB=0,  # ignored for last span
            nf_dB=0,  # ignored for last span
            power_out_dBm=1.0,
            last_span_no_preamp=True,
        )
        assert nsr == pytest.approx(1.3360081534e-3, rel=1e-4)


# ---------------------------------------------------------------------------
# calculate_demand_snr: end-to-end path SNR
# ---------------------------------------------------------------------------
class TestCalculateDemandSNR:
    """Validate the full path SNR calculation (maps to C++ calculateDemandSNR)."""

    def test_single_link_ila_preamp(
        self, single_link_ila_preamp: list[FiberLink]
    ) -> None:
        """80km link, ILA@40km(10dB) + preamp@80km(10dB).

        Expected: SNR ≈ 19.9562 dB, Rx power ≈ -16.00 dBm.
        """
        from src.core.qot_calculator import calculate_demand_snr

        snr_dB, power_dBm = calculate_demand_snr(single_link_ila_preamp)
        assert snr_dB == pytest.approx(19.9562, abs=0.05)
        assert power_dBm == pytest.approx(-16.0, abs=0.1)

    def test_single_link_ila_no_preamp(
        self, single_link_ila_no_preamp: list[FiberLink]
    ) -> None:
        """80km link, ILA@40km(20dB), no preamp.

        Expected: SNR ≈ 22.9485 dB, Rx power ≈ -15.00 dBm.
        """
        from src.core.qot_calculator import calculate_demand_snr

        snr_dB, power_dBm = calculate_demand_snr(single_link_ila_no_preamp)
        assert snr_dB == pytest.approx(22.9485, abs=0.05)
        assert power_dBm == pytest.approx(-15.0, abs=0.1)

    def test_empty_path_raises(self) -> None:
        """Empty path must raise ValueError (mirrors C++ runtime_error)."""
        from src.core.qot_calculator import calculate_demand_snr

        with pytest.raises(ValueError, match="[Ee]mpty|[Ll]ength 0"):
            calculate_demand_snr([])

    def test_trx_noise_floor_is_added(
        self, single_link_ila_preamp: list[FiberLink]
    ) -> None:
        """Verify the 26dB transponder NSR is included in the final SNR.

        The final SNR should be LOWER than the SNR computed from
        optical noise alone (without NSR_Tx).
        """
        from src.core.qot_calculator import calculate_demand_snr

        snr_dB, _ = calculate_demand_snr(single_link_ila_preamp)
        # Without TRX noise: SNR_optical = 10*log10(1/total_NSR)
        # With TRX noise:    SNR_total  = 10*log10(1/(total_NSR + NSR_Tx))
        # SNR_total < SNR_optical always
        # Our reference total_NSR = 7.5894e-3, NSR_Tx = 2.5119e-3
        snr_optical_only = 10 * math.log10(1 / 7.5894296072e-3)
        assert snr_dB < snr_optical_only


# ---------------------------------------------------------------------------
# assess_qot: feasibility check
# ---------------------------------------------------------------------------
class TestAssessQoT:
    """Validate the top-level QoT assessment wrapper."""

    def test_feasible_path(self, single_link_ila_preamp: list[FiberLink]) -> None:
        """Path with SNR=19.96dB and power=-16dBm should be feasible for 100G."""
        from src.core.qot_calculator import assess_qot

        result = assess_qot(single_link_ila_preamp, bitrate_gbps=100)
        assert isinstance(result, QoTResult)
        assert result.feasible is True
        assert result.snr_dB == pytest.approx(19.9562, abs=0.05)
        assert result.power_dBm == pytest.approx(-16.0, abs=0.1)
        assert result.snr_threshold_dB == pytest.approx(8.6)

    def test_unfeasible_due_to_snr(self) -> None:
        """A very long path should fail the SNR threshold for 200G (15.2 dB).

        Using a 200km link with weak amplification.
        """
        from src.core.qot_calculator import assess_qot

        weak_path = [
            FiberLink(
                link_id=0,
                src_node_id=0,
                dst_node_id=1,
                length_km=200,
                amplifiers=[
                    Amplifier(position_km=100, gain_dB=10.0, amp_type="ila"),
                ],
            ),
        ]
        result = assess_qot(weak_path, bitrate_gbps=200)
        # With weak gain over a very long span, SNR should drop below 15.2
        assert result.feasible is False

    def test_unfeasible_due_to_power(self) -> None:
        """A path with heavy loss and no amplification should fail power threshold.

        Single very long link with minimal gain.
        """
        from src.core.qot_calculator import assess_qot

        lossy_path = [
            FiberLink(
                link_id=0,
                src_node_id=0,
                dst_node_id=1,
                length_km=300,
                amplifiers=[
                    Amplifier(position_km=300, gain_dB=10.0, amp_type="preamp"),
                ],
            ),
        ]
        result = assess_qot(lossy_path, bitrate_gbps=100)
        # Power after 300km + node losses - 10dB gain will be well below -18 dBm
        assert result.power_dBm < -18.0
        assert result.feasible is False

    def test_link_with_no_amplifiers(self) -> None:
        """A short link with no EDFAs — only propagation loss, NLI from last span."""
        from src.core.qot_calculator import assess_qot

        short_path = [
            FiberLink(
                link_id=0,
                src_node_id=0,
                dst_node_id=1,
                length_km=10,
                amplifiers=[],
            ),
        ]
        result = assess_qot(short_path, bitrate_gbps=100)
        # Very short, but no amplification means very low power
        assert isinstance(result, QoTResult)
        # Power: 1 - 6 (mux) - 1 (out conn) - 2.5 (10km prop) - 1 (conn) - 6 (demux) = -15.5
        assert result.power_dBm == pytest.approx(-15.5, abs=0.5)


# ---------------------------------------------------------------------------
# Multi-hop path
# ---------------------------------------------------------------------------
class TestMultiHopPath:
    """Validate SNR calculation over multi-link paths."""

    def test_two_link_path(self) -> None:
        """Two-hop path: verifies node loss accumulation at intermediate node."""
        from src.core.qot_calculator import calculate_demand_snr

        path = [
            FiberLink(
                link_id=0,
                src_node_id=0,
                dst_node_id=1,
                length_km=40,
                port_loss_dB=0.5,
                amplifiers=[
                    Amplifier(position_km=40, gain_dB=15.0, amp_type="preamp"),
                ],
            ),
            FiberLink(
                link_id=1,
                src_node_id=1,
                dst_node_id=2,
                length_km=40,
                port_loss_dB=0.5,
                amplifiers=[
                    Amplifier(position_km=40, gain_dB=15.0, amp_type="preamp"),
                ],
            ),
        ]
        snr_dB, power_dBm = calculate_demand_snr(path)
        # Multi-hop must produce lower SNR than single-hop (more accumulated noise)
        snr_single, _ = calculate_demand_snr([path[0]])
        assert snr_dB < snr_single
        # Power should be finite (not -inf)
        assert power_dBm > -50
