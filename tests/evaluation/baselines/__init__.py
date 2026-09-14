"""Comparative Baselines Package for Sprint 4 Evaluation.

Exports the unified polymorphic interface and all baseline implementations:
  - Baseline A: LLMOnlyBaseline (llm_only)
  - Baseline B: AlwaysOnHITLBaseline (always_on)
  - Baseline C: TraditionalSDONBaseline (traditional_sdon)
  - Proposed:   ProposedRADGBaseline (proposed_radg)
"""

from tests.evaluation.baselines.base import (
    STANDARD_FOLLOW_UP_INTENT,
    BaseBaseline,
    BaselineResult,
    get_baseline,
    list_baselines,
    run_baseline,
)
from tests.evaluation.baselines.always_on_hitl import AlwaysOnHITLBaseline
from tests.evaluation.baselines.llm_only import LLMOnlyBaseline
from tests.evaluation.baselines.proposed_radg import ProposedRADGBaseline
from tests.evaluation.baselines.traditional_sdon import TraditionalSDONBaseline

__all__ = [
    "STANDARD_FOLLOW_UP_INTENT",
    "BaseBaseline",
    "BaselineResult",
    "LLMOnlyBaseline",
    "AlwaysOnHITLBaseline",
    "TraditionalSDONBaseline",
    "ProposedRADGBaseline",
    "get_baseline",
    "list_baselines",
    "run_baseline",
]
