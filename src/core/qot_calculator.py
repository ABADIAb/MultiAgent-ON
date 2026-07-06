"""QoT Calculator — GN Model Physics Engine.

Pure-Python port of the C++ QoT functions from Network.cpp:
  - span_snr()           ← C++ spanSNR (L6172-6249)
  - calculate_demand_snr() ← C++ calculateDemandSNR (L4728-5100)
  - assess_qot()         ← Top-level feasibility wrapper

Scope: Filtered (ROADM) network mode only. Filterless ASE propagation
(calculatePropagatedSNR) is deferred to a later iteration.
Equalization loss is assumed zero (all channels at equal launch power).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core.constants import CHANNEL, FIBER, NODE, THRESHOLD
from src.core.models import QoTResult

if TYPE_CHECKING:
    from src.core.models import FiberLink


# ---------------------------------------------------------------------------
# Pre-computed GN model constant (independent of span parameters)
# Mirrors the C++ `constant_nli` computed at the top of spanSNR.
# ---------------------------------------------------------------------------
def _compute_constant_nli() -> float:
    """Compute the NLI constant η₀ from the GN model.

    Formula (from C++ Network.cpp L6176-6177):
        log_func = ln(π²·|β₂|·Rs²·N_ch^(2·Rs/Δf) / α)
        constant_nli = (8/27)·α·γ²·log_func / (π·|β₂|·Rs²)
    """
    alpha = FIBER.alpha_linear
    log_func = math.log(
        math.pi**2
        * abs(FIBER.beta2)
        * CHANNEL.rs_baud**2
        * CHANNEL.n_channels ** (2 * CHANNEL.rs_baud / CHANNEL.spacing_hz)
        / alpha
    )
    return (
        (8.0 / 27.0)
        * alpha
        * FIBER.gamma**2
        * log_func
        / (math.pi * abs(FIBER.beta2) * CHANNEL.rs_baud**2)
    )


_CONSTANT_NLI = _compute_constant_nli()


# ---------------------------------------------------------------------------
# span_snr: per-span SNR computation
# ---------------------------------------------------------------------------
def span_snr(
    fiber_length_km: float,
    gain_dB: float,
    nf_dB: float,
    power_out_dBm: float,
    *,
    last_span_no_preamp: bool = False,
) -> tuple[float, float]:
    """Compute 1/SNR (NSR) for a single amplified span.

    Direct port of C++ ``Network::spanSNR`` (Network.cpp L6172-6249).

    Args:
        fiber_length_km: Effective fiber length contributing to NLI [km].
            This is ``first_subspan_length_km`` in the C++ code — it accounts
            for trans-node spans where only part of the fiber generates NLI.
        gain_dB: EDFA gain [dB]. Ignored when ``last_span_no_preamp=True``.
        nf_dB: EDFA noise figure [dB]. Ignored when ``last_span_no_preamp=True``.
        power_out_dBm: Signal power at the EDFA output [dBm].
            For ``last_span_no_preamp``, this is the current power entering the span.
        last_span_no_preamp: If True, the span has no pre-amplifier (last span).
            Only NLI is computed (no ASE since there's no amplification).

    Returns:
        Tuple of (NSR_linear, power_out_dBm).
    """
    alpha = FIBER.alpha_linear

    # Effective length [m] and NLI coefficient
    fiber_m = fiber_length_km * 1e3
    l_eff = (1 - math.exp(-fiber_m * alpha)) / alpha if fiber_length_km > 0 else 0.0
    nli_coeff = _CONSTANT_NLI * l_eff**2

    if last_span_no_preamp:
        # No amplifier → no ASE. Only NLI.
        power_w = 10 ** (power_out_dBm / 10.0) / 1e3
        nsr_lin = nli_coeff * power_w**2
        return nsr_lin, power_out_dBm

    # Standard amplified span: ASE + NLI
    gain_lin = 10 ** (gain_dB / 10.0)
    nf_lin = 10 ** (nf_dB / 10.0)

    p_ase = CHANNEL.planck_freq_rs * (gain_lin - 1) * nf_lin
    power_w = 10 ** (power_out_dBm / 10.0) / 1e3

    if fiber_length_km == 0:
        # Booster with no preceding fiber: ASE only, no NLI
        nsr_lin = p_ase / power_w
    else:
        nsr_lin = (p_ase + nli_coeff * power_w**3) / power_w

    return nsr_lin, power_out_dBm


# ---------------------------------------------------------------------------
# calculate_demand_snr: full path SNR
# ---------------------------------------------------------------------------
def calculate_demand_snr(path: list[FiberLink]) -> tuple[float, float]:
    """Calculate end-to-end SNR and receiver power for a lightpath.

    Direct port of C++ ``Network::calculateDemandSNR`` (Network.cpp L4728-5100).
    Assumes filtered (non-filterless) network and zero equalization loss.

    Args:
        path: Ordered list of ``FiberLink`` objects forming the lightpath.

    Returns:
        Tuple of (snr_dB, rx_power_dBm).

    Raises:
        ValueError: If the path is empty.
    """
    if not path:
        msg = "Path length 0"
        raise ValueError(msg)

    # Transponder noise floor: 26 dB back-to-back SNR
    nsr_tx_lin = 1.0 / 10 ** (CHANNEL.snr_trx_dB / 10.0)

    total_nsr_lin = 0.0
    current_power_dBm = CHANNEL.tx_power_dBm  # 1 dBm

    # Tracking for trans-node span NLI computation
    prev_fiber_after_last_edfa_km = 0.0
    first_span = True

    for link_idx, link in enumerate(path):
        is_first_link = link_idx == 0
        is_last_link = link_idx == len(path) - 1
        first_loc_on_link = True
        previous_position_km = 0.0

        # --- Node losses at start of link ---
        if is_first_link:
            # First node: mux filter loss
            current_power_dBm -= NODE.filter_loss_dB
        else:
            # Intermediate node: input port connector + port loss
            in_loss = NODE.connector_loss_dB + link.port_loss_dB
            current_power_dBm -= in_loss

        # Equalization loss: zero (Option A — approved)

        # Output port loss: port loss + connector
        out_loss = link.port_loss_dB + NODE.connector_loss_dB
        current_power_dBm -= out_loss

        # --- Process each EDFA on the link ---
        span_loss_dB = 0.0
        last_span = False

        for edfa in link.amplifiers:
            # Fiber propagation from previous position to this EDFA
            span_length_km = edfa.position_km - previous_position_km
            previous_position_km = edfa.position_km

            prop_loss = span_length_km * FIBER.att_coeff_dB_km
            current_power_dBm -= prop_loss
            span_loss_dB += prop_loss

            # Connector before EDFA (not for boosters, type == 1)
            if edfa.amp_type != "booster":
                current_power_dBm -= NODE.connector_loss_dB
                span_loss_dB += NODE.connector_loss_dB

            # Determine effective fiber length for NLI
            if first_loc_on_link:
                # Trans-node span: use leftover fiber from previous link
                effective_fiber_km = prev_fiber_after_last_edfa_km
            else:
                effective_fiber_km = span_length_km

            # Fiber remaining after this EDFA to end of link
            prev_fiber_after_last_edfa_km = link.length_km - edfa.position_km

            # Check if this is the last span (preamp at end of last link)
            if is_last_link and edfa.position_km == link.length_km:
                last_span = True

            # Attenuator before EDFA (if any)
            if edfa.att_dB > 0:
                current_power_dBm -= edfa.att_dB
                span_loss_dB += edfa.att_dB

            # EDFA gain
            current_power_dBm += edfa.gain_dB

            # Determine power_out for span_snr
            power_out = (
                edfa.power_out_dBm
                if edfa.power_out_dBm is not None
                else current_power_dBm
            )

            # Compute span SNR
            nsr, _ = span_snr(
                fiber_length_km=effective_fiber_km,
                gain_dB=edfa.gain_dB,
                nf_dB=edfa.nf_dB,
                power_out_dBm=power_out,
                last_span_no_preamp=False,
            )
            total_nsr_lin += nsr

            first_span = False
            first_loc_on_link = False
            span_loss_dB = 0.0

            if last_span:
                # Drop loss at destination: connector + port + demux filter
                drop_loss = (
                    NODE.connector_loss_dB + link.port_loss_dB + NODE.filter_loss_dB
                )
                current_power_dBm -= drop_loss
                break

            # Connector after EDFA (not for preamps, type == 3)
            if edfa.amp_type != "preamp":
                current_power_dBm -= NODE.connector_loss_dB
                span_loss_dB += NODE.connector_loss_dB

        if last_span:
            break

        # --- Last link, no preamp at end ---
        if is_last_link:
            # Remaining fiber after last EDFA (or full link if no EDFAs)
            if link.amplifiers:
                last_edfa = link.amplifiers[-1]
                remaining_km = link.length_km - last_edfa.position_km
            else:
                remaining_km = link.length_km

            if first_loc_on_link:
                # No EDFAs on this link at all
                # Apply full link propagation loss
                prop_loss = link.length_km * FIBER.att_coeff_dB_km
                current_power_dBm -= prop_loss

                effective_fiber_km = (
                    prev_fiber_after_last_edfa_km if not first_span else link.length_km
                )
            else:
                # Remaining fiber after last EDFA
                if remaining_km > 0:
                    prop_loss = remaining_km * FIBER.att_coeff_dB_km
                    current_power_dBm -= prop_loss

                effective_fiber_km = prev_fiber_after_last_edfa_km

            # Drop losses
            drop_loss = link.port_loss_dB + NODE.filter_loss_dB
            last_span_loss = NODE.connector_loss_dB + drop_loss
            current_power_dBm -= last_span_loss

            # Last span NLI (no preamp → no ASE)
            nsr_last, _ = span_snr(
                fiber_length_km=effective_fiber_km,
                gain_dB=0,
                nf_dB=0,
                power_out_dBm=current_power_dBm + last_span_loss + prop_loss,
                last_span_no_preamp=True,
            )
            total_nsr_lin += nsr_last
            last_span = True
            break

        # --- Fiber after last EDFA to end of link (intermediate link) ---
        if not first_loc_on_link and prev_fiber_after_last_edfa_km > 0:
            prop_loss = prev_fiber_after_last_edfa_km * FIBER.att_coeff_dB_km
            current_power_dBm -= prop_loss

        elif first_loc_on_link:
            # No EDFAs on this intermediate link — full propagation
            prop_loss = link.length_km * FIBER.att_coeff_dB_km
            current_power_dBm -= prop_loss
            prev_fiber_after_last_edfa_km = link.length_km

    # Final SNR: include transponder noise floor
    snr_dB = 10 * math.log10(1.0 / (total_nsr_lin + nsr_tx_lin))

    return snr_dB, current_power_dBm


# ---------------------------------------------------------------------------
# assess_qot: top-level feasibility wrapper
# ---------------------------------------------------------------------------
def assess_qot(
    path: list[FiberLink],
    bitrate_gbps: int = 100,
) -> QoTResult:
    """Assess QoT feasibility of a lightpath.

    Computes SNR and receiver power, then compares against thresholds.

    Args:
        path: Ordered list of ``FiberLink`` objects forming the lightpath.
        bitrate_gbps: Demand bitrate (10, 100, or 200 Gbps).

    Returns:
        ``QoTResult`` with feasibility verdict.
    """
    snr_threshold = THRESHOLD.get_snr_threshold(bitrate_gbps)
    power_threshold = THRESHOLD.prec_threshold_dBm

    snr_dB, power_dBm = calculate_demand_snr(path)

    feasible = snr_dB >= snr_threshold and power_dBm >= power_threshold

    return QoTResult(
        snr_dB=snr_dB,
        power_dBm=power_dBm,
        feasible=feasible,
        snr_threshold_dB=snr_threshold,
        power_threshold_dBm=power_threshold,
    )
