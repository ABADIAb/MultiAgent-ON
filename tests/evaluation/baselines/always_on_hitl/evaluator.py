"""Evaluator for the Always-On HITL baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tests.evaluation.baselines.always_on_hitl.graph import compile_always_on_graph
from tests.evaluation.baselines.common.reporter import save_evaluation_results
from tests.evaluation.baselines.common.runner import evaluate_intent_with_graph


class AlwaysOnHITLEvaluator:
    """Evaluates the Always-On HITL baseline on Nominal intents."""

    def __init__(self, baseline_name: str = "always_on_hitl") -> None:
        self.baseline_name = baseline_name

    def evaluate_single(
        self,
        item: dict[str, Any],
        max_turns: int = 3,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Evaluate a single nominal demand through Always-On HITL."""
        item_copy = dict(item)
        # In Always-On HITL, the expected Turn 1 action is forced to 'clarify'
        item_copy["expected_radg_action"] = "clarify"

        res = evaluate_intent_with_graph(
            graph_factory=compile_always_on_graph,
            item=item_copy,
            max_turns=max_turns,
            baseline_name=self.baseline_name,
            verbose=verbose,
        )
        # Success for Always-On HITL means it intercepted Turn 1 with clarify and reached approve in Turn 2
        res["success"] = (res.get("initial_action") == "clarify" and res.get("final_action") == "approve")
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
        """Evaluate Class I Nominal demands and export telemetry snapshots."""
        nominal_items = [item for item in corpus if item.get("class") == "I_Nominal"]
        if not nominal_items:
            # Fallback if unclassified
            nominal_items = corpus

        if verbose:
            print(f"\n[Always-On HITL] Scoped evaluation to {len(nominal_items)} Nominal demand(s).")

        results = []
        for idx, item in enumerate(nominal_items, 1):
            if verbose:
                print(f"\n>>> [{idx}/{len(nominal_items)}] Processing demand: {item.get('id')}")
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
