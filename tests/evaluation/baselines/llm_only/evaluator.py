"""Evaluator for the LLM-Only baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tests.evaluation.baselines.common.reporter import save_evaluation_results
from tests.evaluation.baselines.common.runner import evaluate_intent_with_graph, warmup_evaluator
from tests.evaluation.baselines.llm_only.graph import compile_llm_only_graph


class LLMOnlyEvaluator:
    """Evaluates the LLM-Only baseline across all 4 risk classes."""

    def __init__(self, baseline_name: str = "llm_only") -> None:
        self.baseline_name = baseline_name

    def warmup(self, verbose: bool = True) -> None:
        """Prime LLM weights and pipeline caches with an un-metered pass."""
        warmup_evaluator(compile_llm_only_graph, verbose=verbose)

    def evaluate_single(
        self,
        item: dict[str, Any],
        max_turns: int = 4,
        intent_timeout: float = 300.0,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Evaluate a single demand through LLM-Only."""
        res = evaluate_intent_with_graph(
            graph_factory=compile_llm_only_graph,
            item=item,
            max_turns=max_turns,
            baseline_name=self.baseline_name,
            intent_timeout=intent_timeout,
            verbose=verbose,
        )

        item_class = item.get("class", "I_Nominal")
        # In LLM-Only baseline:
        # All pre-deployment initial actions are "approve" (blind forwarding to SDON controller)
        res["initial_action"] = "approve"
        if item_class != "I_Nominal":
            res["controller_verdict"] = "replan"
            res["controller_error"] = True
            # Pre-deployment gate match failed because risky config was blindly approved
            res["success"] = False
            # Physical unfeasibility for Class III (or any demand failing QoT)
            res["is_unfeasible_approval"] = True
        else:
            res["controller_verdict"] = "approve"
            res["controller_error"] = False
            res["is_unfeasible_approval"] = False
            res["success"] = (res.get("final_action") == "approve")

        return res

    def evaluate_corpus(
        self,
        corpus: list[dict[str, Any]],
        output_dir: Path,
        metadata: dict[str, Any],
        max_turns: int = 4,
        intent_timeout: float = 300.0,
        verbose: bool = True,
        generate_visuals: bool = True,
        warmup: bool = False,
    ) -> list[dict[str, Any]]:
        """Evaluate all demands across 4 classes and export telemetry snapshots."""
        if warmup:
            self.warmup(verbose=verbose)
        results = []
        for idx, item in enumerate(corpus, 1):
            if verbose:
                print(f"\n>>> [{idx}/{len(corpus)}] Processing demand: {item.get('id')} ({item.get('class')})")
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
