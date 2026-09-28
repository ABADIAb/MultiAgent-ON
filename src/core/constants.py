"""Physical-layer constants for the GN model QoT calculator.

All values extracted from the C++ simulator (Network.h / OaLoc.h)
to ensure exact numerical parity with the original implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class FiberConstants:
    """Standard single-mode fiber (SMF) parameters."""

    gamma: float = 1.27e-3  # Nonlinear coefficient [1/(W·m)]
    beta2: float = 21.7e-27  # GVD parameter [s²/m]
    att_coeff_dB_km: float = 0.25  # Attenuation coefficient [dB/km]

    @property
    def alpha_linear(self) -> float:
        """Attenuation in Neper/m (converted from dB/km)."""
        return self.att_coeff_dB_km / (10.0 * math.log10(math.e)) / 1e3


@dataclass(frozen=True)
class ChannelConstants:
    """WDM channel and transponder parameters."""

    center_freq_hz: float = 193.4e12  # Central frequency [Hz]
    rs_baud: float = 32e9  # Symbol rate [Baud]
    spacing_hz: float = 50e9  # Channel spacing [Hz]
    c_band_hz: float = 5e12  # C-band bandwidth [Hz]
    tx_power_dBm: float = 1.0  # Transponder output power [dBm]
    snr_trx_dB: float = 26.0  # Transponder back-to-back SNR [dB]

    @property
    def n_channels(self) -> float:
        """Number of WDM channels in the C-band."""
        return self.c_band_hz / self.spacing_hz

    @property
    def planck_freq_rs(self) -> float:
        """Pre-computed h·ν·Rs product for ASE noise calculation."""
        planck = 6.62607004e-34  # Planck's constant [J·s]
        return planck * self.center_freq_hz * self.rs_baud


@dataclass(frozen=True)
class NodeConstants:
    """Passive optical node loss parameters."""

    filter_loss_dB: float = 6.0  # Mux/Demux insertion loss [dB]
    connector_loss_dB: float = 1.0  # Fiber connector loss [dB]


@dataclass(frozen=True)
class AmplifierConstants:
    """EDFA amplifier operating parameters and NF model coefficients.

    Characterized by:
      - Booster and ILA: gain range [10, 24] dB (with 1 dB margin -> max 23 dB),
        NF range [6, 12] dB via polynomial a=2.793, b=117.513.
      - Pre-amp: gain range [18, 32] dB,
        NF range [6.2, 10.5] dB via polynomial a=3.88, b=457.586.
    """

    # Gain bounds [dB]
    booster_min_gain_dB: float = 10.0
    booster_max_gain_dB: float = 23.0  # 24 - 1 dB safety margin
    ila_min_gain_dB: float = 10.0
    ila_max_gain_dB: float = 23.0  # 24 - 1 dB safety margin
    preamp_min_gain_dB: float = 18.0
    preamp_max_gain_dB: float = 32.0

    # Noise Figure polynomial model: NF_lin = a + b / (G_lin - 1)
    coeff_a_booster: float = 2.793
    coeff_b_booster: float = 117.513
    coeff_a_preamp: float = 3.88
    coeff_b_preamp: float = 457.586

    # Legacy default aliases for backward compatibility
    coeff_a: float = 2.793
    coeff_b: float = 117.513


@dataclass(frozen=True)
class ThresholdConstants:
    """QoT feasibility thresholds."""

    prec_threshold_dBm: float = -18.0  # Minimum receiver power [dBm]
    snr_threshold_10g_dB: float = 12.2  # SNR threshold for 10G [dB]
    snr_threshold_100g_dB: float = 8.6  # SNR threshold for 100G [dB]
    snr_threshold_200g_dB: float = 15.2  # SNR threshold for 200G [dB]
    snr_threshold_400g_dB: float = 21.5  # SNR threshold for 400G [dB]

    def get_snr_threshold(self, bitrate_gbps: int) -> float:
        """Return the SNR threshold for a given bitrate."""
        thresholds = {
            10: self.snr_threshold_10g_dB,
            100: self.snr_threshold_100g_dB,
            200: self.snr_threshold_200g_dB,
            400: self.snr_threshold_400g_dB,
        }
        if bitrate_gbps not in thresholds:
            msg = (
                f"Unsupported bitrate: {bitrate_gbps}G. "
                f"Supported: {sorted(thresholds.keys())}"
            )
            raise ValueError(msg)
        return thresholds[bitrate_gbps]


# Default instances matching the C++ simulator
FIBER = FiberConstants()
CHANNEL = ChannelConstants()
NODE = NodeConstants()
AMPLIFIER = AmplifierConstants()
THRESHOLD = ThresholdConstants()
