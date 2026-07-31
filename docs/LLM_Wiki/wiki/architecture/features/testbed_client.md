---
title: "Feature: RESTConf Testbed Client"
date: 2026-07-29
tags: [feature, restconf, api, cas, testbed, integration]
status: active
---

# Feature: RESTConf Testbed Client

## 1. Title and Overview
**RESTConfTestbedClient** (`src/services/testbed_client.py`)
This feature serves as the bridge between our Neurosymbolic Orchestrator and the physical (virtualized) SM Optics Optical Network Controller (ONC). Its primary responsibility is to securely authenticate with the controller, discover the optical network elements (NEs) and physical links, and return a deterministic `TopologySnapshot` for the Symbolic Solver to route over.

## 2. How it Works
The client uses the `httpx` library to communicate with the REST NBI of the controller. The most complex part of its operation is the **CAS Single Sign-On (SSO) authentication flow**:
1. The ONC REST NBI operates on port `8443`.
2. Accessing any protected endpoint (like `/onc/nbi/ne`) without a session cookie triggers an HTTP redirect to the CAS server (which internally runs on port `8843`).
3. The `_authenticate_cas` method performs a dummy `GET` to the NBI on `8443`, follows the redirect to the CAS login form, and extracts the `execution` token.
4. It then `POST`s the credentials back to the CAS server, which redirects back to the NBI, seamlessly establishing a `TGC` session cookie in the `httpx` cookie jar.

Once authenticated, the client exposes methods to query NEs and Connections, which are subsequently aggregated by `get_topology()` into a `TopologySnapshot`.

## 3. Requirements/Dependencies
- `httpx` for HTTP requests and cookie management.
- Valid VPN connection to the virtual testbed environment (`10.79.26.48`).
- Valid credentials (`admin`/`admin`).
- Relevent classes: `TopologySnapshot`, `NetworkNode`, `FiberLink` from `src/core/state.py`.

## 4. Inputs and Outputs

### `get_topology()`
- **Input**: None (uses instance configuration like `ne_filter="Qiaolun"`).
- **Output**: `TopologySnapshot` dataclass.
```python
@dataclass
class TopologySnapshot:
    nodes: list[NetworkNode]
    links: list[FiberLink]
    timestamp: str
```

### Note on API Quirks
When querying `/connection` with `connectionType="infrastructure-eth"`, if there are zero physical links provisioned in the controller, the SM Optics API returns a `400 Bad Request` instead of a `200 OK` with an empty array `[]`. The client explicitly catches this `400` error and safely returns `[]` to prevent pipeline crashes.

## 5. Associated Files
- **Implementation**: [src/services/testbed_client.py](file:///home/felipeab/MultiAgentON/src/services/testbed_client.py)
- **Data Structures**: [src/core/state.py](file:///home/felipeab/MultiAgentON/src/core/state.py)
- **Tests**: [tests/integration/test_onc_api.py](file:///home/felipeab/MultiAgentON/tests/integration/test_onc_api.py) and [tests/unit/test_onc_client.py](file:///home/felipeab/MultiAgentON/tests/unit/test_onc_client.py)

## 6. How to Test/Use
You can test the connectivity and topology assembly by running the integration tests suite. The tests use a `scope="class"` fixture to ensure the CAS login is only performed once per test run.

```bash
# Ensure you are connected to the VPN
uv run pytest tests/integration/test_onc_api.py -v -m integration
```
