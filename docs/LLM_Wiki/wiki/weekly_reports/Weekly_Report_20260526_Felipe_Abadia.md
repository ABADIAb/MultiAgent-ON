# Master's Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
LangGraph coding & Post-Meeting Planning

## Date Range:
May 19, 2026 - May 26, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260519_Felipe_Abadia|previous report]]:*
1. **Professor Consultation:** Present both proposals ([[experiments/Proposal_QoT_Integration]] and [[experiments/Proposal_Orchestrator_Integration]]) to the professor.
2. **QoT Implementation Execution:** Begin the translation of the GN model math from `Network.cpp` into `qot_tool.py`.
3. **StateGraph Implementation:** Begin coding the LangGraph `StateGraph` based on the V2 architecture.

---

## 2. Actual Progress This Week

1. **Professor Consultation (Goal 1 — Completed):** Meeting held on May 19 with Prof. Zhang, Zheng, and Aryanaz. Both proposals were presented and discussed. Key feedback received:
   - **Zheng:** Requested 3-5 concrete intent examples showing how the LangGraph pipeline handles different user requests.
   - **Prof. Zhang:** Requested a comparison table/slides summarizing the differences of our approach compared to existing agentic AI works in the literature.
   - **Aryanaz:** Confirmed the testbed fibers are too short for meaningful QoT degradation; the lab is trying to borrow longer fibers.
2. **LangGraph Coding (Goal 3 — Completed):** Built the core graph structure:
   - `src/core/state.py`: `AgentState` TypedDict with SLA, topology, and feasibility fields.
   - `src/core/graph.py`: `StateGraph` with 5 nodes (Supervisor, HITL, Topology, Routing, Lightpath).
   - `src/agents/`: 4 mock agent modules (`supervisor.py`, `topology.py`, `routing.py`, `lightpath.py`).
3. **QoT Implementation Execution** (Goal 2): (Pending)

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access (Persistent).
- **Status:** Still unable to connect directly via SSH.
- **Next Step:** Seek guidance from lab assistants on the specific jump-host or VPN configuration required.

---

## 4. Plan for Next Week

1. **SOTA & Literature Comparison:** Create the comparison table and some slides summarizing the differences of our MultiAgentON approach compared to existing agentic AI systems in the literature (Prof. Zhang's request).
2. **Intent Examples:** Document 3-5 concrete user intent examples showing how the LangGraph pipeline activates different agent sequences (Zheng's request).
3. **Supervisor LLM Integration:** Replace mock code in `supervisor.py` with actual LangChain/LangGraph LLM calls to parse intents into the `sla_matrix`.
4. **Pydantic Schemas:** Study the baseline JSON schemas for Python Pydantic classes implementation.

---

## 5. Do You Need Support?

Write here: Need support to connect to the virtual environment. 

---

## 6. One-Sentence Summary

Held the professor consultation meeting, began coding the LangGraph StateGraph with mock agents, and began to align the V2 architecture with the SOTA comparison and intent examples requested.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
