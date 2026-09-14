# Sprint 4 Evaluation Benchmark: Consolidated Metrics Summary

> Standardized 17-Node Nobel-Germany Core Backbone Topology ($|V|=17, |E|=26$).
> Invariant Proof: **Proposed Neurosymbolic RADG strictly guarantees UAR = 0.0%**.

| Baseline | CRR (%) | CFG-PR (%) | UAR (%) | QFR (%) | PIIR (%) | Latency (s) | Prompt Tokens | Total Tokens | ΔTokens (%) | ΔHITL (%) | GDA (%) | FPR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed (Neurosymbolic RADG)** | 0.0% | 100.0% | 0.0% | 100.0% | 100.0% | 0.05s | 451 | 1256 | 41.4% | 100.0% | 100.0% | 0.0% |
| Baseline A (Monolithic LLM) | 0.0% | 0.0% | 100.0% | 0.0% | 100.0% | 0.00s | 770 | 829 | 0.0% | 100.0% | 100.0% | 0.0% |
| Baseline B (Always-On HITL) | 0.0% | 100.0% | 0.0% | 100.0% | 100.0% | 0.00s | 451 | 511 | 41.4% | 0.0% | 100.0% | 0.0% |
| Baseline C (Always-Off HITL) | 0.0% | 100.0% | 0.0% | 100.0% | 100.0% | 0.00s | 451 | 511 | 41.4% | 100.0% | 100.0% | 0.0% |
| Baseline D (Traditional SDON) | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% | 0.00s | 0 | 0 | 100.0% | 50.0% | 100.0% | 0.0% |

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
