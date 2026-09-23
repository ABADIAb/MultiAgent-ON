"""Evaluator for the LLM-Only baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tests.evaluation.baselines.common.reporter import save_evaluation_results
from tests.evaluation.baselines.common.runner import evaluate_intent_with_graph
from tests.evaluation.baselines.llm_only.graph import compile_llm_only_graph


class LLMOnlyEvaluator:
    """Evaluates the LLM-Only baseline across all 4 risk classes."""

    def __init__(self, baseline_name: str = "llm_only") -> None:
        self.baseline_name = baseline_name

    def evaluate_single(
        self,
        item: dict[str, Any],
        max_turns: int = 3,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Evaluate a single demand through LLM-Only."""
        res = evaluate_intent_with_graph(
            graph_factory=compile_llm_only_graph,
            item=item,
            max_turns=max_turns,
            baseline_name=self.baseline_name,
            verbose=verbose,
        )

        item_class = item.get("class", "I_Nominal")
        # In LLM-Only:
        # Reaching controller on Turn 1 with a non-nominal intent is considered an unsafe/false-positive arrival
        if item_class != "I_Nominal":
            res["is_unfeasible_approval"] = True
            # The gate match failed from a pre-deployment perspective because bad config reached the controller
            res["success"] = (res.get("initial_action") == "replan" and res.get("final_action") == "approve")
        else:
            res["is_unfeasible_approval"] = False
            res["success"] = (res.get("initial_action") == "approve")

        return res

    def evaluate_corpus(
        self,
        corpus: list[dict[str, Any]],
        output_dir: Path,
        metadata: dict[str, Any],
        max_turns: int = 3,
        verbose: bool = True,
        generate_visuals: bool = True,
    ) -> list[dict[str, Any]]:
        """Evaluate all demands across 4 classes and export telemetry snapshots."""
        results = []
        for idx, item in enumerate(corpus, 1):
            if verbose:
                print(f"\n>>> [{idx}/{len(corpus)}] Processing demand: {item.get('id')} ({item.get('class')})")
            res = self.evaluate_single(item, max_turns=max_turns, verbose=verbose)
            results.append(res)

        save_evaluation_results(
            results=results,
            output_dir=output_dir,
            metadata=metadata,
            baseline_id=self.baseline_name,
            generate_visuals=generate_visuals,
        )
        return results
