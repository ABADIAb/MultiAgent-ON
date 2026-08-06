"""QoT Bridge — converts Symbolic Solver path dicts to models.FiberLink objects.

The Symbolic Solver produces candidate paths as plain dicts (using
state.FiberLink topology data). The QoT calculator requires physics-level
models.FiberLink objects with Amplifier Pydantic models.

This module bridges the gap without polluting either layer.

Placement: core/ — pure Python conversion logic, no LLM calls, no framework deps.
"""

from __future__ import annotations

from src.core.models import Amplifier, FiberLink


def candidate_path_to_fiber_links(path: dict) -> list[FiberLink]:
    """Convert a solver candidate path dict into a list of models.FiberLink.

    Each entry in ``path["link_physics"]`` is converted into a ``models.FiberLink``
    with its associated ``Amplifier`` objects. Sequential integer IDs are assigned
    because ``models.FiberLink.link_id`` is typed as int.

    Args:
        path: A candidate path dict from the Symbolic Solver. Must contain a
            ``link_physics`` key with a list of dicts, each having:
              - link_id (str): Original link identifier (used for logging only).
              - length_km (float): Fiber span length.
              - port_loss_dB (float, optional): Node port insertion loss. Default 0.0.
              - amplifiers (list[dict]): EDFA configs matching models.Amplifier fields.

    Returns:
        Ordered list of ``models.FiberLink`` objects ready for ``assess_qot()``.

    Raises:
        KeyError: If ``link_physics`` key is missing from the path dict.
        ValueError: If an amplifier dict fails Pydantic validation.
    """
    link_physics_list: list[dict] = path["link_physics"]

    fiber_links: list[FiberLink] = []
    for idx, physics in enumerate(link_physics_list):
        amplifiers = [
            Amplifier(**amp_dict)
            for amp_dict in physics.get("amplifiers", [])
        ]
        fiber_links.append(
            FiberLink(
                link_id=idx,
                src_node_id=idx,
                dst_node_id=idx + 1,
                length_km=physics["length_km"],
                port_loss_dB=physics.get("port_loss_dB", 0.0),
                amplifiers=amplifiers,
            )
        )

    return fiber_links
