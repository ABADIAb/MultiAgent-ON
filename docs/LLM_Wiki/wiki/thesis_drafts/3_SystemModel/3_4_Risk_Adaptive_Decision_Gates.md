---
title: "Chapter 3 - Section 3.3: The Risk-Adaptive Decision Gates (RADGs)"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, radg, decision-function, usem, qot, hitl, reverse-prompting, interrupt]
status: draft
---

# 3.4 The Risk-Adaptive Decision Gates (RADGs)

## 3.4.1 Mathematical Formulation of the RADGs Decision Function

The principal control logic of the proposed neurosymbolic architecture resides within the Risk-Adaptive Decision Gates (RADGs). Formulated as a deterministic, piecewise decision function $D$, the RADGs evaluate two independent, sequentially computed risk signals to guarantee pre-deployment operational integrity. These signals comprise:

1. **Semantic Uncertainty ($U_{sem} \in [0, 1]$):** A quantifiable metric capturing linguistic ambiguity, unstated network parameters, and structural LLM translation errors.
2. **Physical Transmission Viability ($\text{QoT}_{valid} \in \{0, 1\}$):** A binary indicator of physical feasibility derived analytically via the Gaussian Noise (GN) model.

The RADGs map the joint state space of these variables to an actionable operational space $\mathcal{A} = \{ \text{approve}, \text{clarify}, \text{replan} \}$. Formally, the overarching decision function is defined as:

$$
D\left(U_{sem}, \text{QoT}_{valid}\right) = \begin{cases} 
\text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ 
\text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ 
\text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 
\end{cases}
$$

where the constant $\tau_{sem} \in (0, 1)$ represents the operational semantic tolerance threshold. This parameter is adjustable by the network operator based on their risk profile; a higher $\tau_{sem}$ reduces human interruptions but increases the risk of deploying a semantically misaligned intent. For the purpose of this thesis evaluation, it is calibrated to a default of $\tau_{sem} = 0.30$.

While conceptualized as a unified mathematical function, the software implementation decouples $D$ hierarchically to enforce a fail-fast execution paradigm. Semantic uncertainty ($U_{sem}$) is evaluated exclusively at Phase 3, halting execution prior to complex route computation if $\tau_{sem}$ is exceeded. The subsequent physical viability ($\text{QoT}_{valid}$) is assessed exclusively at Phase 6, ensuring that the GN-model calculations are reserved strictly for semantically verified intents.

<!-- FIGURE_PLACEHOLDER: radg_decision_space -->
> **Figure: Risk-Adaptive Decision Gates (RADGs) 2D Operational State Space** (`figs_SystemModel/pdf/radg_decision_space.pdf`)
> Visual representation of the piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$. The horizontal axis denotes Semantic Uncertainty $U_{sem} \in [0, 1]$ with threshold delimiter $\tau_{sem} = 0.30$; the vertical axis represents the physical margin $\Delta\text{GSNR} = \text{GSNR}_{path} - \text{GSNR}_{th}$ (dB). The partitioned state space maps directly to three operational action zones: Zone I: Auto-Approve (top-left, safe), Zone II: Suggest Replan (bottom-left, infeasible physics), and Zone III: Early HITL Clarify (right, high ambiguity with physics simulation bypassed).

---

## 3.4.2 Two-Layer Semantic Uncertainty Quantification ($U_{sem}$)

To prevent false positives during automated intent translation, $U_{sem}$ undergoes a two-layer hierarchical assessment. 

#### Layer 1: Structural CFG Validity ($v_{struct}$)

The generated Planning Domain Definition Language (PDDL) constraint block $\mathcal{S}_{PDDL}$ is evaluated against a deterministic Context-Free Grammar $\mathcal{G}_{pddl}$, while verifying node existence against the active topology subgraph $V_{sub}$:

$$
v_{struct} = \begin{cases} 1 & \text{if } \mathcal{S}_{PDDL} \in \mathcal{L}(\mathcal{G}_{pddl}) \land \text{EndpointsExist}(\mathcal{S}_{PDDL}, V_{sub}) \\ 0 & \text{otherwise} \end{cases}
$$

#### Layer 2: Reverse Prompting Semantic Divergence ($d_{sem}$)

To prevent semantic drift and enforce formal semantic convergence, the architecture implements Reverse Prompting as a closed-loop validation contract.

<!-- FIGURE_PLACEHOLDER: reverse_prompting_loop -->
> **Figure: Closed-Loop Reverse Prompting Validation condition** (`figs_SystemModel/pdf/reverse_prompting_loop.pdf`)
> Closed-loop verification cycle enforcing semantic convergence: the operator's natural language intent $\mathcal{I}_{NL}$ is translated into formal PDDL predicates $\mathcal{S}_{PDDL}$, independently reconstructed back to natural language $\mathcal{I}_{recon}$, and evaluated for semantic divergence $d_{sem}$.

Assuming $v_{struct} = 1$, the formal PDDL specification is reconstructed into a natural language confirmation statement $\mathcal{I}_{recon}$ via an independent Reverse Prompting mechanism. The semantic divergence $d_{sem} \in [0, 1]$ is computed directly by a dedicated evaluator LLM that scores the semantic discrepancy between the original operator request $\mathcal{I}_{NL}$ and the algorithmic reconstruction $\mathcal{I}_{recon}$:

$$
d_{sem} = \text{Score}_{divergence}\left( \mathcal{I}_{NL}, \mathcal{I}_{recon} \right)
$$

where $0.0$ indicates perfect semantic alignment and $1.0$ indicates total constraint loss.

#### Composite $U_{sem}$ Evaluation

The composite uncertainty metric combines both layers into a strict fail-fast formulation. Structural grammar violations immediately maximize uncertainty, neutralizing downstream processing:

$$
U_{sem} = \begin{cases} 1.0 & \text{if } v_{struct} = 0 \\ d_{sem} & \text{if } v_{struct} = 1 \end{cases}
$$

---

## 3.4.3 Deterministic Physical-Layer QoT Evaluation

Following semantic validation, physical feasibility is assessed deterministically utilizing the analytical coherent Gaussian Noise (GN) model for uncompensated optical fiber transmission.

### Optical Signal-to-Noise Ratio (Amplified Spontaneous Emission)

Within each fiber span $m$ comprising link $e_{ij}$, Erbium-Doped Fiber Amplifiers (EDFAs) introduce Amplified Spontaneous Emission (ASE) noise. The ASE noise power within the optical reference bandwidth (set to the symbol rate $R_s$) is defined as:

$$
P_{ASE, m} = (G_m - 1) \cdot h \nu \cdot R_s \cdot NF_m
$$

where $h$ is Planck's constant ($6.626 \times 10^{-34} \text{ J}\cdot\text{s}$), $\nu$ represents the optical carrier frequency ($193.1 \text{ THz}$), $G_m$ dictates the linear amplifier gain compensating for span attenuation, and $NF_m$ is the specific amplifier noise figure. 

Consequently, the linear inverse Optical Signal-to-Noise Ratio attributable to ASE over link $e_{ij}$ containing $M$ discrete spans is:

$$
\text{OSNR}_{ASE}^{-1}(e_{ij}) = \sum_{m=1}^M \frac{P_{ASE, m}}{P_{ch}}
$$

where $P_{ch}$ denotes the launch channel power expressed in Watts.

### Non-Linear Interference (NLI) Modeling

Under the coherent GN model paradigm, Non-Linear Interference (NLI) generated by Kerr non-linearities—specifically Self-Phase Modulation and Cross-Phase Modulation—is approximated as an additive Gaussian noise disturbance. The specific analytical GN-model formulation utilized computes the uncompensated NLI power as:

$$
\eta_0 = \frac{8}{27} \frac{\alpha \gamma^2}{\pi |\beta_2| R_s^2} \ln\left( \frac{\pi^2 |\beta_2| R_s^2 N_{ch}^{2 R_s / \Delta f}}{\alpha} \right)
$$

$$
P_{NLI, m} = \eta_0 L_{eff}^2 P_{ch}^3
$$

where $\gamma$ specifies the fiber non-linear coefficient, $\beta_2 = -\frac{\lambda^2}{2\pi c} D$ characterizes the group velocity dispersion parameter (directly linked to the topological chromatic dispersion $D$), $R_s$ is the transmitted symbol rate, $N_{ch}$ is the channel count, $\Delta f$ is the channel spacing, and $L_{eff} = \frac{1 - e^{-\alpha L_m}}{\alpha}$ represents the effective non-linear fiber length for linear attenuation $\alpha$. The associated non-linear signal-to-noise ratio contribution is thus formulated as:

$$
\text{SNR}_{NLI}^{-1}(e_{ij}) = \sum_{m=1}^M \frac{P_{NLI, m}}{P_{ch}}
$$

### Generalized SNR (GSNR) Accumulation

The aggregate Generalized Signal-to-Noise Ratio characterizing a candidate path $\pi = (e_1, e_2, \dots, e_H)$ is calculated by accumulating the inverse linear SNR contributions across all cascaded links:

$$
\text{GSNR}(\pi)^{-1} = \sum_{h=1}^H \left( \text{OSNR}_{ASE}^{-1}(e_h) + \text{SNR}_{NLI}^{-1}(e_h) \right)
$$

Converted to a standard logarithmic decibel scale, the final measurement is expressed as:

$$
\text{GSNR}_{dB}(\pi) = 10 \log_{10}\left( \frac{1}{\text{GSNR}(\pi)^{-1}} \right)
$$

### Binary QoT Feasibility Indicator

The final physical viability of the proposed paths is evaluated against the required modulation design threshold $\text{GSNR}_{th}$:

$$
\text{QoT}_{valid} = \begin{cases} 1 & \text{if } \exists \pi \in \mathcal{K}_{path} \text{ such that } \text{GSNR}_{dB}(\pi) \ge \text{GSNR}_{th} \land P_{rx}(\pi) \ge P_{rx,min} \\ 0 & \text{otherwise} \end{cases}
$$

---

## 3.4.4 Decision Matrix and Action Execution Policies

The mathematical intersection of the semantic and physical risk signals maps deterministically to the RADGs operational decision matrix:

| $U_{sem}$ Evaluation | $\text{QoT}_{valid}$ Status | RADGs Decision | Pipeline Action & Human Engagement |
| :--- | :--- | :--- | :--- |
| $\le \tau_{sem}$ | $1$ (Feasible) | Approve | Auto-provision (Zero Human Interaction) |
| $\le \tau_{sem}$ | $0$ (Infeasible) | Replan | HITL Interrupt: Suggest relaxing constraints |
| $> \tau_{sem}$ | N/A (Bypassed) | Clarify | HITL Interrupt: Clarify semantic ambiguity |

---

## 3.4.5 Constraint Preservation and Convergence Guarantees

To ensure multi-turn refinement strictly terminates, the architecture defines a **Constraint Preservation** condition. Let $\mathcal{C}_k$ denote the set of active hard constraints during iteration $k$. Following operator feedback $\mathcal{F}_k$, the subsequent constraint set satisfies:

$$\mathcal{C}_{k+1} = \mathcal{C}_k \cup \text{ExtractConstraints}(\mathcal{F}_k) \setminus \text{ExplicitRevocations}(\mathcal{F}_k)$$

Maintaining $\mathcal{C}_k$ within a structured state dictionary rather than unstructured conversational history provides two analytical guarantees. First, established operational rules cannot degrade silently; they require explicit operator revocation. Second, the architecture strictly bounds the maximum number of clarification turns to $N_{max} = 3$. If an intent fails to achieve $U_{sem} \le \tau_{sem}$ after $N_{max}$ iterations, the system halts execution, preventing control-plane deadlocks.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.3 Placement (The 2D Decision Space Diagram):** 
> To maximize academic clarity, insert a visual representation of the RADGs state space mapping immediately following Section 3.3.1. 
> - **X-axis:** Semantic Uncertainty $U_{sem} \in [0, 1]$ with a solid vertical delimiter representing $\tau_{sem} = 0.30$.
> - **Y-axis:** GSNR Margin defined as $\Delta\text{GSNR} = \text{GSNR}_{computed} - \text{GSNR}_{th}$ ($\text{dB}$), featuring a solid horizontal delimiter at $0\text{ dB}$.
> - **Quadrants:** Shade and label the three distinct operational zones: the **Clarify Zone** ($U_{sem} > 0.30$), the **Replan Zone** ($\Delta\text{GSNR} < 0$), and the **Auto-Approve Zone** (top-left, safe).

> [!TIP]
> **Equation Cross-Reference Tracking:** 
> When assembling Chapter 4 (Implementation), ensure you cross-reference the theoretical formulas presented in Section 3.4.3 with the exact algorithmic constants defined inside your `src/core/constants.py` and `src/core/qot_calculator.py` files. Aligning the Greek variables here to your Python variable names creates an airtight link between theory and software.
