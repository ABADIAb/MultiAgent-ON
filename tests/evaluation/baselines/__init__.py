"""Baseline architectures and evaluation harness for comparative benchmarking."""

from __future__ import annotations

from tests.evaluation.baselines.always_on_hitl import (
    AlwaysOnHITLEvaluator,
    compile_always_on_graph,
)
from tests.evaluation.baselines.llm_only import (
    LLMOnlyEvaluator,
    compile_llm_only_graph,
)
from tests.evaluation.baselines.proposed_radg import (
    ProposedRADGEvaluator,
    compile_proposed_graph,
)

__all__ = [
    "AlwaysOnHITLEvaluator",
    "LLMOnlyEvaluator",
    "ProposedRADGEvaluator",
    "compile_always_on_graph",
    "compile_llm_only_graph",
    "compile_proposed_graph",
]
