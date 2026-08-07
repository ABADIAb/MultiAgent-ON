"""Data models for the QoT calculator.

Pure Pydantic models representing network topology elements needed
for QoT assessment. These decouple the physics engine from the C++
object hierarchy (Unifiber, OaLoc, Node).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Amplifier(BaseModel):
    """Represents an EDFA on a fiber link.

    Attributes:
        position_km: Distance from the start of the link [km].
        gain_dB: EDFA gain [dB].
        nf_dB: Noise figure [dB]. If not provided, it will be computed
            from the gain using the polynomial NF model.
        amp_type: Amplifier type — booster (1), ILA (2), or preamp (3).
        att_dB: Attenuator loss before the EDFA [dB].
        power_out_dBm: Output power after amplification [dBm].
            If not provided, power is tracked from the transponder.
    """

    position_km: float = Field(ge=0)
    gain_dB: float = Field(gt=0)
    nf_dB: float | None = None
    amp_type: Literal["booster", "ila", "preamp"]
    att_dB: float = Field(default=0.0, ge=0)
    power_out_dBm: float | None = None

    @model_validator(mode="after")
    def compute_nf_if_missing(self) -> Amplifier:
        """Compute NF from gain using the polynomial model if not provided."""
        if self.nf_dB is None:
            import math

            from src.core.constants import AMPLIFIER

            gain_lin = 10 ** (self.gain_dB / 10.0)
            nf_lin = AMPLIFIER.coeff_a + AMPLIFIER.coeff_b / (gain_lin - 1)
            self.nf_dB = 10.0 * math.log10(nf_lin)
        return self

    def __getitem__(self, item: str) -> Any:
        """Allow dict-like indexing for backwards compatibility."""
        return getattr(self, item)


class FiberLink(BaseModel):
    """A unidirectional fiber link connecting two nodes in the topology.

    Canonical model for both topology layer and QoT physics engine.

    Attributes:
        link_id: Unique identifier for the link (string or int coerced to str).
        source_node: Source node identifier (e.g. 'Milano-A' or '1').
        target_node: Destination node identifier (e.g. 'Milano-B' or '2').
        length_km: Total fiber length [km].
        num_amplifiers: Number of EDFAs on this link.
        active_channels: Number of active WDM channels.
        port_loss_dB: Node port insertion loss [dB].
        amplifiers: EDFAs on this link, ordered by position_km.
    """

    link_id: str | int
    source_node: str = ""
    target_node: str = ""
    length_km: float = Field(gt=0)
    num_amplifiers: int = 0
    active_channels: int = 0
    port_loss_dB: float = Field(default=0.0, ge=0)
    amplifiers: list[Amplifier] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: dict | Any) -> dict | Any:
        """Normalize legacy aliases (src_node_id, dst_node_id, link_id int)."""
        if isinstance(data, dict):
            data = dict(data)
            if "link_id" in data and not isinstance(data["link_id"], str):
                data["link_id"] = str(data["link_id"])
            if "source_node" not in data and "src_node_id" in data:
                data["source_node"] = str(data["src_node_id"])
            if "target_node" not in data and "dst_node_id" in data:
                data["target_node"] = str(data["dst_node_id"])
        return data

    @property
    def src_node_id(self) -> str:
        """Alias for physics engine compatibility."""
        return self.source_node

    @property
    def dst_node_id(self) -> str:
        """Alias for physics engine compatibility."""
        return self.target_node

    @model_validator(mode="after")
    def validate_amplifier_positions(self) -> FiberLink:
        """Ensure amplifiers are within the link and sorted by position."""
        for amp in self.amplifiers:
            if amp.position_km > self.length_km:
                msg = (
                    f"Amplifier at {amp.position_km} km exceeds "
                    f"link length {self.length_km} km"
                )
                raise ValueError(msg)
        self.amplifiers = sorted(self.amplifiers, key=lambda a: a.position_km)
        if self.amplifiers:
            self.num_amplifiers = len(self.amplifiers)
        return self


class QoTResult(BaseModel):
    """Output of the QoT assessment.

    Attributes:
        snr_dB: Computed Signal-to-Noise Ratio at receiver [dB].
        power_dBm: Received optical power [dBm].
        feasible: Whether the path meets both SNR and power thresholds.
        snr_threshold_dB: The SNR threshold used for feasibility check [dB].
        power_threshold_dBm: The receiver power threshold [dBm].
    """

    snr_dB: float
    power_dBm: float
    feasible: bool
    snr_threshold_dB: float
    power_threshold_dBm: float = -18.0
