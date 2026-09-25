"""Evaluator for Proposed Neurosymbolic RADG baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tests.evaluation.baselines.common.reporter import save_evaluation_results
from tests.evaluation.baselines.common.runner import evaluate_intent_with_graph, warmup_evaluator
from tests.evaluation.baselines.proposed_radg.graph import compile_proposed_graph


class ProposedRADGEvaluator:
    """Evaluates the Proposed Neurosymbolic RADG pipeline across all 4 risk classes."""

    def __init__(self, baseline_name: str = "proposed_radg") -> None:
        self.baseline_name = baseline_name

    def warmup(self, verbose: bool = True) -> None:
        """Prime LLM weights and pipeline caches with an un-metered pass."""
        warmup_evaluator(compile_proposed_graph, verbose=verbose)

    def evaluate_single(
        self,
        item: dict[str, Any],
        max_turns: int = 3,
        intent_timeout: float = 300.0,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Evaluate a single demand through the Proposed RADG pipeline."""
        return evaluate_intent_with_graph(
            graph_factory=compile_proposed_graph,
            item=item,
            max_turns=max_turns,
            baseline_name=self.baseline_name,
            intent_timeout=intent_timeout,
            verbose=verbose,
        )

    def evaluate_corpus(
        self,
        corpus: list[dict[str, Any]],
        output_dir: Path,
        metadata: dict[str, Any],
        max_turns: int = 3,
        intent_timeout: float = 300.0,
        verbose: bool = True,
        generate_visuals: bool = True,
        warmup: bool = False,
    ) -> list[dict[str, Any]]:
        """Evaluate a list of demands and export telemetry snapshots."""
        if warmup:
            self.warmup(verbose=verbose)
        results = []
        for idx, item in enumerate(corpus, 1):
            if verbose:
                print(f"\n>>> [{idx}/{len(corpus)}] Processing demand: {item.get('id')}")
            res = self.evaluate_single(item, max_turns=max_turns, intent_timeout=intent_timeout, verbose=verbose)
            results.append(res)

        save_evaluation_results(
            results=results,
            output_dir=output_dir,
            metadata=metadata,
            baseline_id=self.baseline_name,
            generate_visuals=generate_visuals,
        )
        return results
