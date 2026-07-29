---
title: "Presentation Proposal: Testbed Integration & Symbolic Solver"
date: 2026-07-29
tags: [presentation, proposal, testbed, symbolic-solver]
status: active
---

# Presentation Proposal

---

## Slide 1: Progress Update: Testbed & Solver Integration

> [!LAYOUT]
> Title centered. Bullet points on the left. A screenshot of the terminal showing 179 passing tests on the right.

- **Milestone Reached:** Successfully integrated the live SM Optics ONC testbed.
- **Authentication Solved:** Handled complex CAS SSO redirection across multiple controller ports.
- **Symbolic Solver Active:** Replaced LLM hallucination with deterministic Yen's K-Shortest Paths.
- **Testing:** 100% test coverage (172 Unit, 7 Live Integration).

<!-- Speaker Notes: Good morning. Today we want to present a major milestone in our architecture. We have successfully hooked our orchestrator into the live SM Optics virtual testbed. We resolved the SSO authentication flow and implemented our deterministic Symbolic Solver, fully eliminating LLM routing hallucination. -->

---

## Slide 2: The Physical Topology Challenge

> [!LAYOUT]
> Two-column layout. Left: Bullet points outlining the current status. Right: A conceptual diagram showing Nodes without Links.

- **Nodes Discovered:** Successfully mapped the `Qiaolun` topology (Terminal, ROADM1, ROADM2).
- **The Block:** Zero physical connections (`infrastructure-eth`) are currently provisioned.
- **API Quirks Handled:** Pipeline gracefully handles 400 Bad Request responses for empty inventory.
- **Action Required:** Need DWDM physical links provisioned in the ONC to demonstrate live routing.

<!-- Speaker Notes: While we successfully discovered the network elements, we noticed that there are no physical optical connections provisioned in the controller's database yet. Our system handles this gracefully, but to demonstrate end-to-end intent routing, we will need those links provisioned in the lab. -->

---

## Slide 3: Querying Optical Physics

> [!LAYOUT]
> Title centered. A large Question box or callout highlighting the core dilemma regarding physics parameters.

- **Architecture V5 Requirement:** We need physical metrics (SNR, fiber length, amplifiers) to trigger the Binary Physical Gate.
- **Current Limitation:** The current REST payload does not expose these physical layer properties.
- **Proposed Solution:** 
  1. Are there alternative API endpoints for extracting QoT parameters?
  2. If not, should we proceed using hardcoded ECOC-realistic values as a proxy?

<!-- Speaker Notes: Finally, our Risk-Adaptive Decision Gate relies on physical physics properties to assess feasibility. Since the current API endpoints do not expose fiber metrics or SNR, we'd like to discuss the best approach moving forward: discovering new endpoints, or relying on our mocked ECOC-realistic values. -->

---
