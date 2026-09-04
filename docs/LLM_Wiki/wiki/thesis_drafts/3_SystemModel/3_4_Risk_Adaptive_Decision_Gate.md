---
title: "Chapter 3 - Section 3.4: The Risk-Adaptive Decision Gate (RADG)"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, radg, decision-function, usem, qot, gn-model, optical-physics]
status: draft
---

# 3.4 The Risk-Adaptive Decision Gate (RADG)

## 3.4.1 Mathematical Formulation of the RADG Decision Function

The principal control logic of the proposed neurosymbolic architecture resides within the Risk-Adaptive Decision Gate (RADG). Formulated as a deterministic, piecewise decision function $D$, the RADG evaluates two orthogonal, sequentially computed risk signals to guarantee pre-deployment safety. These signals comprise:

1. **Semantic Uncertainty ($U_{sem} \in [0, 1]$):** A quantifiable metric capturing linguistic ambiguity, unstated network parameters, and structural LLM translation errors.
2. **Physical Transmission Viability ($\text{QoT}_{valid} \in \{0, 1\}$):** A binary indicator of physical feasibility derived analytically via the uncompensated Gaussian Noise (GN) model.

The RADG maps the joint state space of these variables to an actionable operational space $\mathcal{A} = \{ \text{approve}, \text{clarify}, \text{replan} \}$. Formally, the overarching decision function is defined as:

$$
D\left(U_{sem}, \text{QoT}_{valid}\right) = \begin{cases} 
\text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ 
\text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ 
\text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 
\end{cases}
$$

where the constant $\tau_{sem} \in (0, 1)$ represents the operational semantic tolerance threshold, calibrated empirically for this architecture to $\tau_{sem} = 0.30$. 

While conceptualized as a unified mathematical function, the software implementation decouples $D$ hierarchically to enforce a fail-fast execution paradigm. Semantic uncertainty ($U_{sem}$) is evaluated exclusively at Phase 3, halting execution prior to complex route computation if $\tau_{sem}$ is exceeded. The subsequent physical viability ($\text{QoT}_{valid}$) is assessed exclusively at Phase 6, ensuring that the computationally expensive GN-model calculations are reserved strictly for semantically verified intents.

---

## 3.4.2 Two-Layer Semantic Uncertainty Quantification ($U_{sem}$)

To prevent false positives during automated intent translation, $U_{sem}$ undergoes a two-layer hierarchical assessment. 

### Layer 1: Structural CFG Validity ($v_{struct}$)

The generated Planning Domain Definition Language (PDDL) constraint block $\mathcal{S}_{PDDL}$ is evaluated against a deterministic Context-Free Grammar $\mathcal{G}_{pddl}$, while verifying node existence against the active topology subgraph $V_{sub}$:

$$
v_{struct} = \begin{cases} 1 & \text{if } \mathcal{S}_{PDDL} \in \mathcal{L}(\mathcal{G}_{pddl}) \land \text{EndpointsExist}(\mathcal{S}_{PDDL}, V_{sub}) \\ 0 & \text{otherwise} \end{cases}
$$

### Layer 2: Reverse Prompting Semantic Divergence ($d_{sem}$)

Assuming $v_{struct} = 1$, the formal PDDL specification is reconstructed into a natural language confirmation statement $\mathcal{I}_{recon}$ via an independent Reverse Prompting mechanism. The semantic divergence $d_{sem}$ is computed as the complement of the cross-encoder agreement score:

$$
d_{sem} = 1 - \text{Score}_{agreement}\left( \mathcal{I}_{NL}, \mathcal{I}_{recon} \right)
$$

where $\mathcal{I}_{NL}$ is the original operator request and $\text{Score}_{agreement} \in [0, 1]$ represents the normalized semantic similarity between the original intent and its algorithmic reconstruction.

### Composite $U_{sem}$ Evaluation

The composite uncertainty metric combines both layers into a strict fail-fast formulation. Structural grammar violations immediately maximize uncertainty, neutralizing downstream processing:

$$
U_{sem} = \begin{cases} 1.0 & \text{if } v_{struct} = 0 \\ d_{sem} & \text{if } v_{struct} = 1 \end{cases}
$$

---

## 3.4.3 Deterministic Physical-Layer QoT Evaluation

Following semantic validation, physical feasibility is assessed deterministically utilizing the analytical coherent Gaussian Noise (GN) model for uncompensated optical fiber transmission.

### Optical Signal-to-Noise Ratio (Amplified Spontaneous Emission)

Within each fiber span $m$ comprising link $e_{ij}$, Erbium-Doped Fiber Amplifiers (EDFAs) introduce Amplified Spontaneous Emission (ASE) noise. The ASE noise power within an optical reference bandwidth $B_{ref}$ is defined as:

$$
P_{ASE, m} = (G_m - 1) \cdot h \nu \cdot NF_m \cdot B_{ref}
$$

where $h$ is Planck's constant ($6.626 \times 10^{-34} \text{ J}\cdot\text{s}$), $\nu$ represents the optical carrier frequency ($193.1 \text{ THz}$), $G_m$ dictates the linear amplifier gain compensating for span attenuation, and $NF_m$ is the specific amplifier noise figure. 

Consequently, the linear inverse Optical Signal-to-Noise Ratio attributable to ASE over link $e_{ij}$ containing $M$ discrete spans is:

$$
\text{OSNR}_{ASE}^{-1}(e_{ij}) = \sum_{m=1}^M \frac{P_{ASE, m}}{P_{ch}}
$$

where $P_{ch}$ denotes the launch channel power expressed in Watts.

### Non-Linear Interference (NLI) Modeling

Under the coherent GN model paradigm, Non-Linear Interference (NLI) generated by Kerr non-linearities—specifically Self-Phase Modulation and Cross-Phase Modulation—is approximated as an additive Gaussian noise disturbance:

$$
P_{NLI, m} \approx \frac{3 \gamma^2 P_{ch}^3 \cdot \ln\left( \pi^2 |\beta_2| B_{ch}^2 L_{eff} \right)}{2 \pi \alpha |\beta_2|}
$$

where $\gamma$ specifies the fiber non-linear coefficient, $\beta_2$ characterizes the group velocity dispersion parameter, $B_{ch}$ is the transmitted symbol rate, and $L_{eff} = \frac{1 - e^{-2\alpha L_m}}{2\alpha}$ represents the effective non-linear fiber length. The associated non-linear signal-to-noise ratio contribution is thus formulated as:

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

The ultimate physical viability of a routed candidate path set $\mathcal{K}_{path}$ is subsequently evaluated against a strict modulation-dependent design threshold $\text{GSNR}_{th}$:

$$
\text{QoT}_{valid} = \begin{cases} 1 & \text{if } \exists \pi \in \mathcal{K}_{path} \text{ such that } \text{GSNR}_{dB}(\pi) \ge \text{GSNR}_{th} \land P_{rx}(\pi) \ge P_{rx,min} \\ 0 & \text{otherwise} \end{cases}
$$

---

## 3.4.4 Decision Matrix and Action Execution Policies

The mathematical intersection of the semantic and physical risk signals maps deterministically to the RADG operational decision matrix:

| $U_{sem}$ Evaluation | $\text{QoT}_{valid}$ Status | RADG Decision | Pipeline Action & Human Engagement |
| :--- | :--- | :--- | :--- |
| **$U_{sem} > \tau_{sem}$** | *Bypassed* | **`clarify`** | **Early HITL Clarification:** Halts execution prior to topology extraction. Queries the operator directly to resolve missing constraints or syntactic translation ambiguities. |
| **$U_{sem} \le \tau_{sem}$** | $\text{QoT}_{valid} = 0$ | **`replan`** | **Physical Risk HITL:** Signals an unfeasible physics state. Halts execution, presenting the inadequate GSNR margins and requesting permission to relax specific constraints. |
| **$U_{sem} \le \tau_{sem}$** | $\text{QoT}_{valid} = 1$ | **`approve`** | **Autonomous Auto-Approval:** Implements zero-friction validation. Compiles the verified routing report and prepares the physical configuration for automated controller provisioning. |

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.4 Placement (The 2D Decision Space Diagram):** 
> To maximize academic clarity, insert a visual representation of the RADG state space mapping immediately following Section 3.4.1. 
> - **X-axis:** Semantic Uncertainty $U_{sem} \in [0, 1]$ with a solid vertical delimiter representing $\tau_{sem} = 0.30$.
> - **Y-axis:** GSNR Margin defined as $\Delta\text{GSNR} = \text{GSNR}_{computed} - \text{GSNR}_{th}$ ($\text{dB}$), featuring a solid horizontal delimiter at $0\text{ dB}$.
> - **Quadrants:** Shade and label the three distinct operational zones: the **Clarify Zone** ($U_{sem} > 0.30$), the **Replan Zone** ($\Delta\text{GSNR} < 0$), and the **Auto-Approve Zone** (top-left, safe).

> [!TIP]
> **Equation Cross-Reference Tracking:** 
> When assembling Chapter 4 (Implementation), ensure you cross-reference the theoretical formulas presented in Section 3.4.3 with the exact algorithmic constants defined inside your `src/core/constants.py` and `src/core/qot_calculator.py` files. Aligning the Greek variables here to your Python variable names creates an airtight link between theory and software.
