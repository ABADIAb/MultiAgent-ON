---
title: "Issue Report 2026-07-10"
date: 2026-07-10
tags: [issue, report, testbed, restconf]
status: active
---

# Issue Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach

## Date: 
2026-07-10

---

## 1. Solved Issues

### Issue 1: C++ to Python QoT translation
- **Issue:** The original C++ GN-model simulator was documented, but a pure Python equivalent was necessary to run smoothly as a deterministic LangChain tool for the MVP.
- **What has already been tried:** We mapped the constants and polynomial NF computations from `Network.h` and `OaLoc.cpp`. Hand-computed GN model reference values were extracted to serve as baselines.
- **Result:** **SOLVED**. The translation was successfully maintained through the Architecture V4 refactor, preserving 100% test coverage.

---

## 2. Pending Issues

### Issue 2: RESTConf Hook to Virtual Testbed
- **Issue:** We need to verify the provisioning hook to the virtual testbed before full LangGraph integration (Blocks Experiment 1.3).
- **What has already been tried:** We identified that the testbed uses RESTConf (not SSH) and operates in a virtual environment. I implemented a structural `RESTConfTestbedClient` stub in Python to interface with it, but the exact endpoints are still missing.
- **Result:** PENDING (Blocks Exp 1.3).
- **Estimated possible solution:** Await the professor's response with the specific virtual testbed API documentation (URL, Authentication, and Topology Endpoints). Once received, I will complete the `get_topology` and `health_check` methods.

---

## 3. Do I Need Support?

Write here: Yes, I need the professor to provide the API documentation (Base URL, Authentication, and Topology Endpoints) for the virtual RESTConf testbed to complete Exp 1.3.

---

## 4. One-Sentence Summary

I successfully resolved the C++ QoT translation integration into the new architecture, leaving only the virtual testbed RESTConf API details pending from the professor to unblock Sprint 1.

---

## 5. Self-Check Before Submission

- [x] I have detailed the issue clearly
- [x] I have written what has already been tried
- [x] I have written the result of what has been tried
- [x] I have written the estimated possible solution
- [x] I have indicated whether I need support
