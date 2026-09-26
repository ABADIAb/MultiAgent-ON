# LLM-Only Baseline Specification: Un-Gated Neural Translation & Controller Error Trace Injection

---

## 1. Executive Summary & Thesis Context

This document defines the architectural specification, operational mechanics, and empirical metrics for the **LLM-Only** baseline within the comparative evaluation framework of the Master's thesis:
> *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*

In contemporary literature on LLM-assisted Software-Defined Optical Networking (SDON), naive intent translation frameworks frequently operate without formal pre-deployment decision gates. They rely entirely on the generative language model to translate natural language into deployment commands, forwarding them blindly to the SDN controller:
$$\mathcal{A}_{pre}^{\text{LLM-Only}} = \{\text{approve}\}, \quad \forall \mathcal{I} \in \mathcal{U}_{intents}$$

This baseline models the **Ablation of Pre-Deployment Risk Governance**:
1. **Semantic Gate Bypassed:** Phase 3 Semantic Gate calculates the semantic uncertainty metric $U_{sem}$ strictly for diagnostic telemetry, but unconditionally sets `usem_passed = True`, completely suppressing the human-in-the-loop (`hitl_clarify`) edge.
2. **Controller-Level Physical Failure:** When unverified, ambiguous, or physically unfeasible lightpaths reach the network controller surrogate (Phase 6), the controller detects SLA or physical impairment violations and aborts provisioning.
3. **RFC 8040 RESTConf Error Injection:** Instead of receiving a clean, structured operator prompt, the LLM is forced to consume raw RESTConf JSON error logs (`mock_restconf_error.json`) emitted by the controller, empirically exposing the token overhead and hallucination risk of autonomous self-repair.

---

## 2. Architectural Formulation & 3-Turn Incident Recovery Lifecycle

The execution lifecycle of the LLM-Only baseline spans three distinct operational turns when processing risky or non-nominal intents:

```mermaid
flowchart TD
    subgraph Turn1 [Turn 1: Blind Forwarding & Controller Abort]
        T1_P1["Phase 1: Intent Ingestion & GraphRAG"] --> T1_P2["Phase 2: Initial PDDL Translation"]
        T1_P2 --> T1_P3["Phase 3: Bypassed Semantic Gate (No HITL)"]
        T1_P3 --> T1_P4["Phase 4: Symbolic K-SP Solver"]
        T1_P4 --> T1_P5["Phase 5: QoT Physics Evaluation"]
        T1_P5 --> T1_Ctrl{"Phase 6: SDON Controller Surrogate"}
        T1_Ctrl -->|"Nominal Feasible"| T1_P7["Phase 7: Planning Report"]
        T1_Ctrl -->|"Physical / Semantic Violation"| T1_Reject["Controller Rejection: Inject RFC 8040 RESTConf Error Log"]
    end

    subgraph Turn2 [Turn 2: Autonomous Blind Retry & Token Inflation]
        T1_Reject -->|"Autonomous Loop (No Human Interrupt)"| T2_P2["Phase 2: PDDL Translation (Consuming Raw JSON Error)"]
        T2_P2 --> T2_P3["Phase 3: Bypassed Semantic Gate"]
        T2_P3 --> T2_P4["Phase 4: Symbolic K-SP Solver"]
        T2_P4 --> T2_P5["Phase 5: QoT Physics Evaluation"]
        T2_P5 --> T2_Ctrl{"Phase 6: SDON Controller Surrogate"}
        T2_Ctrl -->|"Blind Self-Repair Failed"| T2_Interrupt["HITL Alarm: Operator Incident Response Required (interrupt)"]
    end

    subgraph Turn3 [Turn 3: Human Incident Response & Recovery]
        T2_Interrupt -->|"Human Operator Injects Nominal Intent"| T3_P2["Phase 2: PDDL Re-Translation (Nominal Recovery)"]
        T3_P2 --> T3_P3["Phase 3: Bypassed Semantic Gate"]
        T3_P3 --> T3_P4["Phase 4: Symbolic K-SP Solver"]
        T3_P4 --> T3_P5["Phase 5: QoT Physics Evaluation"]
        T3_P5 --> T3_Ctrl{"Phase 6: SDON Controller Surrogate"}
        T3_Ctrl -->|"Approved"| T3_P7["Phase 7: Final Synthesis & Planning Report"]
    end
```

### 2.1 Turn 1: Blind Forwarding & Controller Abort
- **Action:** Initial intent is ingested and translated. Phase 3 bypasses operator confirmation regardless of $U_{sem}$.
- **Controller Reaction:** For Class I (Nominal), if feasible, the controller provisions directly. For non-nominal traffic (Classes II, III, IV), the controller surrogate aborts deployment.
- **Error Injection:** The controller node loads `mock_restconf_error.json` (RFC 8040 RESTConf error payload detailing calculated GSNR vs. threshold violations, ASE noise accumulation at amplifier stages, and PCE path rejection).
- **No Human Interrupt:** Rather than calling `interrupt()`, the system injects the raw error string into `state["messages"]`, sets `error_context`, and routes directly back to `pddl_parser` (`radg_decision = "replan"`).

### 2.2 Turn 2: Autonomous Blind Retry & Token Inflation
- **LLM Token Penalty:** The LLM receives the full raw JSON error trace embedded in its context window. It attempts to diagnose physical impairment metrics (e.g., OSNR penalty, EDFA noise figures) and generate corrected PDDL constraints.
- **Hallucination & Failure:** Because the underlying intent is fundamentally ambiguous, physically unreachable, or adversarial, blind prompt manipulation cannot resolve the physical bottleneck.
- **Incident Escalation:** Upon evaluating the Turn 2 lightpaths, the controller surrogate confirms persistent constraint failure. At this stage, execution triggers `interrupt()`, demanding human operator intervention.

### 2.3 Turn 3: Human Incident Response & Safe Recovery
- **Incident Response:** The network operator intervenes, acknowledging production failure and providing a verified nominal recovery intent (e.g., standard rerouting with feasible GSNR).
- **Provisioning:** The pipeline compiles the operator's replacement intent, validates physical reachability, and concludes with an approved Phase 7 deployment report.

---

## 3. Four Core Validation Pillars: Ablation Telemetry

| Validation Pillar | Evaluated Metric | Theoretical Target | LLM-Only Performance | Architectural Diagnosis |
| :--- | :--- | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | $100.0\%$ | Retains explicit constraints on nominals |
| | CFG Pass Rate (CFG-PR) | $\ge 95\%$ | $100.0\%$ | Regex grammar validator active |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.85$ | N/A (Bypassed) | Semantic gate validation bypassed |
| | Ambiguity / Adversarial Catch | $100\%$ | **$0.0\%$** | Completely fails to catch upstream ambiguity |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **$100.0\%$** (Severe Penalty) | Pushes unfeasible or ambiguous lightpaths directly to production |
| | Physical Infeasibility Catch (PIIR) | $100\%$ | **$0.0\%$** | Zero pre-deployment interception |
| **Pillar 3: Efficiency & Friction** | Mean E2E Latency ($T_{E2E}$) | Contextual | **$13.2\text{s} - 16.5\text{s}$** | Inflated by 3-turn multi-pass streaming |
| | Cumulative Token Footprint | Monitored | **$\approx 3\times$ Proposed** | Consumes raw RESTConf error JSON traces |
| | Nominal HITL Interrupts | $0$ | **$0$** (100% Efficiency) | Zero operator friction on benign nominals |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $> 98\%$ | **$25.0\%$** (Catastrophic) | Only nominals match expected pre-deployment approve |
| | False Positive Rate (FPR) | **$0.0\%$** | **$100.0\%$** (Total Failure) | 100% of risky intents pushed to controller |

---

## 4. Orthogonal Radar Coordinates

When mapped to the **Four Orthogonal Radar Axes (0 to 100, 100 optimal)**:

1. **Pre-Deployment Integrity ($100 - FPR$):** **$0.0\%$**
   - Total collapse ($FPR=100\%$). $100\%$ of risky/unfeasible/adversarial intents are blindly approved by the pre-deployment pipeline without pre-flight gating.
2. **Zero-Touch Autonomy:** **$25.0\%$**
   - Only 25% of traffic provisions touchlessly; 75% triggers emergency human intervention upon controller rejection.
3. **Speed:** **$\approx 33.3\%$**
   - Severely penalized due to multi-pass streaming across Turn 1 (blind push) and Turn 2 (blind retry).
4. **Token Usage:** **$\approx 25.0\%$**
   - Severely penalized due to ingesting verbose RFC 8040 RESTConf error payloads in Phase 2 prompts.

---

## 5. Artifacts, Visual Figures & Architectural Justifications

All baseline telemetry and executive visual figures are generated in `tests/evaluation/baselines/llm_only/results/<LLM>/<timestamp>/`:
- `evaluation_results.json`: Comprehensive telemetry traces (controller rejection codes, RESTConf error payloads, token usage).
- `evaluation_results.csv`: Flat tabular export.
- `evaluation_summary.md`: Four Pillars executive markdown report.
- `llm_only_ablation_dashboard.png / .pdf`: 16:9 widescreen master ablation dashboard for thesis presentations.

*(Note: Cross-baseline comparative figures such as `comparative_deployment_flow_sankey.png / .pdf` and `comparative_pillars_breakdown.png / .pdf` are generated in the global comparative results directory `tests/evaluation/results/<LLM>/<timestamp>/`).*

### 5.1 Testbed Artifacts
- `mock_restconf_error.json`: Authoritative RFC 8040 RESTConf error payload simulating optical physical-layer reach failure, ASE noise accumulation, and PCE path computation rejection.

