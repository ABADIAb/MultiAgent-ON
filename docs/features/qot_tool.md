# QoT Tool (Quality of Transmission Calculator)

## Overview
The **QoT Tool** is a pure-Python Quality of Transmission (QoT) feasibility calculator designed to assess whether an optical lightpath can successfully transmit data. It acts as a deterministic physical-layer engine for the LangGraph orchestrator, eliminating the need for the LLM to hallucinate complex SNR (Signal-to-Noise Ratio) or GN-model calculations.

It evaluates candidate lightpaths against strictly defined physical constraints (SNR threshold and receiver power threshold) to guarantee they are viable before provisioning.

## How it Works
The physics engine is a direct port of the C++ GN-model simulator (specifically `Network::spanSNR` and `Network::calculateDemandSNR`). 
- **GN Model:** It computes both linear Amplified Spontaneous Emission (ASE) noise from EDFAs and nonlinear interference (NLI) generated in the fiber.
- **Node & Span Propagation:** It tracks the signal power [dBm] as it traverses nodes (filter and connector losses) and fiber spans (propagation attenuation and EDFA gain).
- **Assessment:** It returns the final SNR [dB] and receiver power [dBm] and compares them against predefined constants for specific bitrates (e.g., 100 Gbps requires 8.6 dB SNR).

*(Note: Currently assumes a filtered network with ROADMs and zero equalization loss).*

## Requirements & Dependencies
- **Pydantic**: Used for strict data validation of the optical elements (`FiberLink`, `Amplifier`).
- **LangChain Core**: The tool is exposed via the `@tool` decorator, making it directly consumable by LangGraph agents.
- **Python 3.x**: Relies on standard library `math`.

## Inputs and Outputs

### Inputs
The LangChain tool `qot_check` expects a dictionary format representing the path:
- `path` (list[dict]): A list of fiber links, each containing:
  - `link_id` (int)
  - `src_node_id` (int)
  - `dst_node_id` (int)
  - `length_km` (float)
  - `port_loss_dB` (float, optional)
  - `amplifiers` (list[dict], optional)
    - `position_km` (float)
    - `gain_dB` (float)
    - `amp_type` (str): `"booster"`, `"ila"`, or `"preamp"`
    - `nf_dB` (float, optional - auto-computed if omitted)
    - `att_dB` (float, optional)
- `bitrate_gbps` (int, optional): The demand bitrate (10, 100, or 200). Defaults to 100.

### Outputs
A dictionary containing the feasibility verdict:
```json
{
  "feasible": true,
  "snr_dB": 12.5,
  "power_dBm": -14.2
}
```
If an error occurs (e.g., unsupported bitrate or invalid topology), it returns:
```json
{
  "error": "Unsupported bitrate: 400G..."
}
```

## Associated Files
- `src/tools/qot_tool.py`: The LangChain `@tool` wrapper (`qot_check`).
- `src/core/qot_calculator.py`: The core pure-Python GN-model physics engine (`assess_qot`, `calculate_demand_snr`, `span_snr`).
- `src/core/models.py`: Pydantic data models (`FiberLink`, `Amplifier`, `QoTResult`) for decoupling input parsing from the physics engine.
- `src/core/constants.py`: Physical-layer constants (fiber attenuation, C-band parameters, EDFA noise polynomial coefficients, thresholds) mapped exactly from the C++ source.

## How to Test/Use
The feature was developed under Strict TDD, so you can verify its functionality using `pytest`.

**Run the test suite:**
```bash
pytest tests/test_qot_calculator.py -v
pytest tests/test_qot_tool.py -v
```

**Usage Example in Python:**
```python
from src.tools.qot_tool import qot_check

candidate_path = [
    {
        "link_id": 1,
        "src_node_id": 0,
        "dst_node_id": 1,
        "length_km": 50.0,
        "amplifiers": [
            {"position_km": 0.0, "gain_dB": 15.0, "amp_type": "booster"},
            {"position_km": 50.0, "gain_dB": 15.0, "amp_type": "preamp"}
        ]
    }
]

result = qot_check.invoke({"path": candidate_path, "bitrate_gbps": 100})
print(result)
```
