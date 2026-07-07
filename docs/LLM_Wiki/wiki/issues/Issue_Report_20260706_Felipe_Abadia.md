---
title: "Issue Report 2026-07-06"
date: 2026-07-06
tags: [issue, report, qot, testbed]
status: active
---

# Issue Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach

## Date: 
2026-07-06

---

## 1. Solved Issues

### Issue 1: C++ to Python QoT translation
- **Issue:** The original C++ GN-model simulator was documented, but a pure Python equivalent was necessary to run smoothly as a deterministic LangChain tool for the MVP.
- **What has already been tried:** We mapped the constants and polynomial NF computations from `Network.h` and `OaLoc.cpp`. Hand-computed GN model reference values were extracted to serve as baselines.
- **Result:** **SOLVED**. The translation was successfully achieved using a rigorous Strict TDD process (30 passing tests, 95% coverage).
- **Solution Applied:** The GN-model equations (`spanSNR`, `calculateDemandSNR`) were ported into `qot_calculator.py` and wrapped in a `@tool` decorator (`qot_tool.py`), successfully closing Experiment 1.1 and 1.2.

---

## 2. Pending Issues

### Issue 2: SSH Hook to Physical Testbed
- **Issue:** We need to verify the provisioning hook to the physical (or simple mock) testbed before full LangGraph integration.
- **What has already been tried:** We have the `MockTestbedClient` working locally as a dictionary, but real-world remote provisioning via SSH is untested.
- **Result:** PENDING (Blocks Experiment 1.3).
- **Estimated possible solution:** Write a secure Python Paramiko adapter to connect via SSH to the simple testbed. The goal is to prove we can fetch the real topology and push configurations via NETCONF/RESTConf.

---

## 3. Do You Need Support?

Write here: I need the professor to provide the "known-good" testing scenarios for the QoT GN model so I can execute the final validation of the Python port against the original C++ outputs.

---

## 4. One-Sentence Summary

I successfully translated and tested the Python QoT calculator (resolving the main tooling blocker), leaving only the SSH testbed connection pending for Sprint 1.

---

## 5. Self-Check Before Submission

- [x] I have detailed the issue clearly
- [x] I have written what has already been tried
- [x] I have written the result of what has been tried
- [x] I have written the estimated possible solution
- [x] I have indicated whether I need support
