---
title: "QoT Awareness"
date: 2026-05-03
tags: [concepts, architecture, physical-layer]
status: active
---
# QoT (Quality of Transmission) Awareness

QoT Awareness refers to the process of verifying that generated light paths (optical routes) are physically feasible for data transmission across the network before establishing them. It ensures that the signal reaches the destination with sufficient quality to be decodable.

## Key Feasibility Criteria

A light path is considered feasible if it satisfies two primary physical-layer constraints at the destination node:

1. **Receiver Power Threshold:** The optical power of the received signal must be greater than **-18 dB**.
2. **SNR (Signal-to-Noise Ratio):** The signal quality at the destination must exceed a specific, defined threshold (`SNR_thresh`).

## Evaluation Model

- **Network-Based Calculation:** QoT metrics are not evaluated in a vacuum node-by-node. The calculation is strictly **network-based**, meaning it accounts for the entire light path, the specific fibers the signal traverses, and the accumulated transmission impairments along the way.
- **GN Model:** The evaluation leverages the **Gaussian Noise (GN) model** to estimate the impact of these transmission impairments and calculate the final SNR across the network.

## Agent Orchestration Context

For the MultiAgentON system, the Orchestrator and Routing Agents will treat the QoT evaluation as a deterministic "black box". The agents do not need to model the complex physical layer phenomena or the optical amplifiers directly. They simply pass the proposed paths to the QoT tool, which validates them against the `-18 dB` power threshold and the SNR threshold, returning a feasibility status.
