# Sprint 4 Evaluation Benchmark: Consolidated Metrics Summary

> Standardized 17-Node Nobel-Germany Core Backbone Topology ($|V|=17, |E|=26$).
> Invariant Proof: **Proposed Neurosymbolic RADG strictly guarantees UAR = 0.0%**.

| Baseline | CRR (%) | CFG-PR (%) | UAR (%) | QFR (%) | PIIR (%) | Latency (s) | Prompt Tokens | ΔTokens (%) | ΔHITL (%) | GDA (%) | FPR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed (Neurosymbolic RADG)** | 55.0% | 51.4% | 0.0% | 100.0% | 100.0% | 0.03s | 593 | 23.3% | 50.6% | 73.8% | 0.0% |
| Baseline A (Monolithic LLM) | 0.0% | 0.0% | 89.0% | 11.0% | 0.0% | 0.00s | 774 | 0.0% | 100.0% | 26.2% | 68.3% |
| Baseline B (Always-On HITL) | 55.0% | 51.4% | 0.0% | 100.0% | 100.0% | 0.00s | 593 | 23.3% | 0.0% | 99.1% | 0.0% |
| Baseline C (Always-Off HITL) | 55.0% | 51.4% | 43.9% | 56.1% | 3.7% | 0.00s | 593 | 23.3% | 100.0% | 26.2% | 48.1% |
| Baseline D (Traditional SDON) | 81.2% | 0.0% | 0.0% | 100.0% | 100.0% | 0.00s | 0 | 100.0% | 34.0% | 44.9% | 0.0% |

### Metric Definitions & Target Invariants
- **CRR (Constraint Retention Rate):** Percentage of operator constraints preserved in PDDL. (Target: 100%)
- **CFG-PR (Context-Free Grammar Pass Rate):** PDDL AST structural validity. (Target: 100% on valid, 0% on adversarial)
- **UAR (Unsafe Approval Rate):** Physically infeasible paths receiving `approve`. (**Absolute Target: 0.0%**)
- **QFR (QoT Feasibility Rate):** Ratio of approved paths that satisfy GSNR threshold under GN-model physics. (Target: 100%)
- **PIIR (Physical Infeasibility Interception Rate):** Class III infeasible demands routed to `replan`. (Target: 100%)
- **ΔTokens (%):** Prompt token reduction achieved by Scoped Optical GraphRAG vs Baseline A. (Target: > 75%)
- **ΔHITL (%):** Operator interruption reduction vs Always-On HITL baseline. (Target: > 70%)
- **GDA (Gate Decision Accuracy):** Alignment with optimal RADG decision state. (Target: > 98%)
- **FPR (False Positive Rate):** Unsafe or ambiguous intents approved. (Target: 0.0%)
