"""Base abstractions, contracts, and shared utilities for evaluation baselines.

Sprint 4: Evaluation Environment & Baseline Testing.
Provides:
  - BaselineResult: Standardized output schema for all evaluated systems.
  - BaseBaseline: Abstract base class defining the run(intent_data) interface.
  - Registry & polymorphic dispatch (get_baseline, run_baseline, list_baselines).
  - Token counting and ground-truth physical feasibility helper.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal, TypedDict

import tiktoken

from src.core.models import FiberLink
from src.core.qot_calculator import assess_qot
from src.services.testbed_client import MockTestbedClient


# ---------------------------------------------------------------------------
# Output Schema Contract
# ---------------------------------------------------------------------------


class BaselineResult(TypedDict, total=False):
    """Standardized output dictionary produced by every baseline run."""

    intent_id: str
    baseline_id: str
    action: Literal["approve", "clarify", "replan", "reject"]
    selected_path: list[str] | None
    computed_gsnr_dB: float | None
    qot_feasible: bool | None
    pddl_valid: bool | None
    parsed_constraints: dict[str, Any] | None
    hitl_interrupts: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    execution_time_s: float
    planning_report: str | None
    error: str | None
    metadata: dict[str, Any]


# ---------------------------------------------------------------------------
# Base Baseline ABC
# ---------------------------------------------------------------------------


class BaseBaseline(ABC):
    """Abstract base class for all comparative evaluation baselines."""

    name: str = "Base Baseline"
    baseline_id: str = "base"

    def __init__(self, **kwargs: Any) -> None:
        self.config = kwargs
        self.topology_snapshot = MockTestbedClient().get_topology()
        self._tokenizer = tiktoken.get_encoding("cl100k_base")

    @abstractmethod
    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        """Execute the baseline against a single intent record from test_corpus.json.

        Args:
            intent_data: Dict with keys: id, class, intent_text, ground_truth_constraints, etc.
            **kwargs: Additional runtime parameters (e.g., timeout, simulated_human).

        Returns:
            BaselineResult dictionary complying with the standardized schema.
        """
        raise NotImplementedError

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the standard cl100k_base tokenizer."""
        if not text:
            return 0
        try:
            return len(self._tokenizer.encode(text))
        except Exception:
            return len(text.split())

    def verify_optical_path(
        self,
        path: list[str] | None,
        min_gsnr_dB: float = 15.0,
        bitrate_gbps: int = 100,
    ) -> tuple[float | None, bool]:
        """Evaluate an optical path against the ground-truth GN-model physics engine.

        Returns:
            (computed_gsnr_dB, is_feasible)
        """
        if not path or len(path) < 2:
            return None, False

        from src.core.mock_graphrag import build_adjacency_graph
        from src.core.symbolic_solver import _build_path_dict, _resolve_node_id

        graph = build_adjacency_graph(self.topology_snapshot)
        resolved_nodes = []
        for name in path:
            node_id = _resolve_node_id(graph, name)
            if not node_id:
                return None, False
            resolved_nodes.append(node_id)

        # Check if consecutive nodes are connected in topology
        for u, v in zip(resolved_nodes[:-1], resolved_nodes[1:]):
            if not graph.has_edge(u, v):
                return None, False

        path_dict = _build_path_dict(graph, resolved_nodes)
        fiber_links = [FiberLink(**p) for p in path_dict.get("link_physics", [])]
        if not fiber_links:
            return None, False

        res = assess_qot(
            path=fiber_links,
            bitrate_gbps=bitrate_gbps,
            target_snr_dB=min_gsnr_dB,
        )
        return round(res.snr_dB, 3), res.feasible


# ---------------------------------------------------------------------------
# Registry & Polymorphic Dispatch
# ---------------------------------------------------------------------------

_BASELINES_REGISTRY: dict[str, type[BaseBaseline]] = {}


def register_baseline(cls: type[BaseBaseline]) -> type[BaseBaseline]:
    """Class decorator to register an evaluation baseline."""
    if not cls.baseline_id:
        raise ValueError(
            f"Baseline class {cls.__name__} must define a non-empty 'baseline_id'."
        )
    _BASELINES_REGISTRY[cls.baseline_id] = cls
    return cls


def get_baseline(baseline_id: str, **kwargs: Any) -> BaseBaseline:
    """Instantiate a registered baseline by ID."""
    if baseline_id not in _BASELINES_REGISTRY:
        available = list(_BASELINES_REGISTRY.keys())
        raise KeyError(f"Unknown baseline_id: '{baseline_id}'. Available: {available}")
    return _BASELINES_REGISTRY[baseline_id](**kwargs)


def list_baselines() -> list[str]:
    """List all registered baseline identifiers."""
    return list(_BASELINES_REGISTRY.keys())


def run_baseline(
    baseline_id: str,
    intent_data: dict[str, Any],
    **kwargs: Any,
) -> BaselineResult:
    """Polymorphic runner helper to instantiate and execute a baseline on intent_data."""
    baseline = get_baseline(baseline_id, **kwargs)
    return baseline.run(intent_data, **kwargs)
