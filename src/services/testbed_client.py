"""Testbed client abstraction and implementations.

Provides a clean interface for testbed communication that can be swapped
between a mock (for development/testing) and the real ONC REST client
(for lab connectivity).
"""

from __future__ import annotations

import logging
import re
import warnings
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx

from src.core.state import FiberLink, NetworkNode, TopologySnapshot

logger = logging.getLogger(__name__)

# Default fiber physical parameters for the Qiaolun testbed topology.
# These are ECOC 2024 paper-based realistic defaults since the ONC NBI
# does not expose raw DWDM physical-layer parameters (spans, amplifiers).
_DEFAULT_LINK_PHYSICS: dict[str, dict] = {
    "default": {
        "length_km": 25.0,
        "num_amplifiers": 1,
        "active_channels": 4,
    }
}


class TestbedClient(ABC):
    """Abstract interface for testbed communication."""

    @abstractmethod
    def get_topology(self) -> TopologySnapshot:
        """Fetch the current network topology from the testbed."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the testbed is reachable."""
        ...


def _build_link_amplifiers(length_km: float) -> list[dict]:
    """Generate realistic EDFA amplifier placements for a fiber link.

    Places:
      - Booster at 0.0 km (gain calibrated to compensate node mux/connector loss)
      - Inline Amplifiers (ILAs) every ~60-80 km for links > 55 km
      - Preamp at destination (at length_km)
    """
    amps: list[dict] = [
        {
            "position_km": 0.0,
            "gain_dB": 3.0,
            "amp_type": "booster",
            "att_dB": 0.0,
        }
    ]

    if length_km <= 55.0:
        # Single span: Preamp at end
        span_loss = length_km * 0.25 + 1.0  # att_coeff (0.25 dB/km) + connector (1.0 dB)
        amps.append({
            "position_km": round(length_km, 1),
            "gain_dB": round(span_loss, 2),
            "amp_type": "preamp",
            "att_dB": 0.0,
        })
    else:
        # Multi-span: target span length ~70 km
        num_spans = max(2, round(length_km / 70.0))
        span_len = length_km / num_spans
        for i in range(1, num_spans):
            pos = i * span_len
            ila_gain = span_len * 0.25 + 2.0  # span att + 2 connectors
            amps.append({
                "position_km": round(pos, 1),
                "gain_dB": round(ila_gain, 2),
                "amp_type": "ila",
                "att_dB": 0.0,
            })
        # Preamp at destination
        last_span_loss = span_len * 0.25 + 1.0
        amps.append({
            "position_km": round(length_km, 1),
            "gain_dB": round(last_span_loss, 2),
            "amp_type": "preamp",
            "att_dB": 0.0,
        })
    return amps


class MockTestbedClient(TestbedClient):
    """Mock testbed client returning the 17-node Nobel-Germany optical backbone topology.

    Standard benchmark topology from SNDlib (17 nodes, 26 bidirectional links).
    Nodes represent major German core optical centers:
      Hannover, Frankfurt, Hamburg, Norden, Bremen, Berlin, Munich, Ulm,
      Nuremberg, Stuttgart, Karlsruhe, Mannheim, Essen, Dortmund, Dusseldorf,
      Cologne, Leipzig.

    Amplifier configurations are generated with physical EDFA placements:
      - Booster at 0.0 km
      - Inline Amplifiers (ILAs) every ~60-80 km
      - Preamp at destination (L km)
    """

    def get_topology(self) -> TopologySnapshot:
        """Return the 17-node Nobel-Germany optical backbone topology."""
        nodes = [
            NetworkNode(node_id="node_1", name="Hannover", interfaces=[101, 102, 103, 104, 105, 106]),
            NetworkNode(node_id="node_2", name="Frankfurt", interfaces=[201, 202, 203, 204, 205]),
            NetworkNode(node_id="node_3", name="Hamburg", interfaces=[301, 302, 303]),
            NetworkNode(node_id="node_4", name="Norden", interfaces=[401, 402]),
            NetworkNode(node_id="node_5", name="Bremen", interfaces=[501, 502, 503]),
            NetworkNode(node_id="node_6", name="Berlin", interfaces=[601, 602, 603]),
            NetworkNode(node_id="node_7", name="Munich", interfaces=[701, 702]),
            NetworkNode(node_id="node_8", name="Ulm", interfaces=[801, 802]),
            NetworkNode(node_id="node_9", name="Nuremberg", interfaces=[901, 902, 903, 904]),
            NetworkNode(node_id="node_10", name="Stuttgart", interfaces=[1001, 1002, 1003]),
            NetworkNode(node_id="node_11", name="Karlsruhe", interfaces=[1101, 1102]),
            NetworkNode(node_id="node_12", name="Mannheim", interfaces=[1201, 1202]),
            NetworkNode(node_id="node_13", name="Essen", interfaces=[1301, 1302]),
            NetworkNode(node_id="node_14", name="Dortmund", interfaces=[1401, 1402, 1403, 1404]),
            NetworkNode(node_id="node_15", name="Dusseldorf", interfaces=[1501, 1502]),
            NetworkNode(node_id="node_16", name="Cologne", interfaces=[1601, 1602, 1603]),
            NetworkNode(node_id="node_17", name="Leipzig", interfaces=[1701, 1702, 1703, 1704]),
        ]

        # 26 standard physical bidirectional links of Nobel-Germany topology
        raw_links_spec = [
            ("link_hannover_berlin", "node_1", "node_6", 324.7, 8),
            ("link_hannover_bremen", "node_1", "node_5", 132.7, 6),
            ("link_hannover_dortmund", "node_1", "node_14", 242.7, 8),
            ("link_hannover_frankfurt", "node_1", "node_2", 341.2, 10),
            ("link_hannover_hamburg", "node_1", "node_3", 169.4, 8),
            ("link_hannover_leipzig", "node_1", "node_17", 275.8, 8),
            ("link_frankfurt_cologne", "node_2", "node_16", 188.9, 8),
            ("link_frankfurt_leipzig", "node_2", "node_17", 381.9, 10),
            ("link_frankfurt_mannheim", "node_2", "node_12", 95.3, 6),
            ("link_frankfurt_nuremberg", "node_2", "node_9", 246.8, 8),
            ("link_hamburg_berlin", "node_3", "node_6", 330.9, 10),
            ("link_hamburg_bremen", "node_3", "node_5", 129.7, 6),
            ("link_norden_bremen", "node_4", "node_5", 156.5, 4),
            ("link_norden_dortmund", "node_4", "node_14", 303.0, 6),
            ("link_berlin_leipzig", "node_6", "node_17", 196.7, 8),
            ("link_munich_nuremberg", "node_7", "node_9", 193.2, 8),
            ("link_munich_ulm", "node_7", "node_8", 154.4, 6),
            ("link_ulm_stuttgart", "node_8", "node_10", 95.9, 6),
            ("link_nuremberg_leipzig", "node_9", "node_17", 298.3, 8),
            ("link_nuremberg_stuttgart", "node_9", "node_10", 212.7, 8),
            ("link_stuttgart_karlsruhe", "node_10", "node_11", 78.7, 6),
            ("link_karlsruhe_mannheim", "node_11", "node_12", 69.8, 6),
            ("link_essen_dortmund", "node_13", "node_14", 44.4, 4),
            ("link_essen_dusseldorf", "node_13", "node_15", 37.5, 4),
            ("link_dortmund_cologne", "node_14", "node_16", 95.3, 6),
            ("link_dusseldorf_cologne", "node_15", "node_16", 48.1, 4),
        ]

        links = [
            FiberLink(
                link_id=link_id,
                source_node=src,
                target_node=dst,
                length_km=length_km,
                num_amplifiers=len(_build_link_amplifiers(length_km)),
                active_channels=channels,
                port_loss_dB=0.5,
                amplifiers=_build_link_amplifiers(length_km),
            )
            for link_id, src, dst, length_km, channels in raw_links_spec
        ]

        return TopologySnapshot(
            nodes=nodes,
            links=links,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def health_check(self) -> bool:
        """Mock always returns True."""
        return True


class RESTConfTestbedClient(TestbedClient):
    """REST client for the SM Optics ONC NBI (Exp 1.3).

    Connects to the optical network controller at the lab testbed and
    retrieves the topology of the 'Qiaolun' sub-topology. The controller
    hosts two topologies; only NEs whose name contains ne_filter are used.

    The ONC NBI (base path /onc/nbi) exposes:
      - GET /ne                → Network Element inventory
      - GET /connection        → Infrastructure/service connections

    Physical fiber parameters (length_km, amplifiers) are NOT available
    from this NBI — they default to realistic ECOC paper values.

    Args:
        base_url: Controller base URL (e.g. 'https://10.79.26.48').
        username: HTTP Basic Auth username.
        password: HTTP Basic Auth password.
        ne_filter: Keyword to filter NEs by name (default: 'Qiaolun').
        link_physics: Optional dict mapping connection names to physical
            parameters. Falls back to _DEFAULT_LINK_PHYSICS['default'].
    """

    _NBI_PREFIX = "/onc/nbi"

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        ne_filter: str = "Qiaolun",
        link_physics: dict | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._ne_filter = ne_filter
        self._link_physics = link_physics or _DEFAULT_LINK_PHYSICS

        # Suppress SSL verification warning once at construction time
        warnings.warn(
            f"RESTConfTestbedClient: SSL verification is disabled for {base_url}. "
            "Acceptable for MVP lab environment only.",
            UserWarning,
            stacklevel=2,
        )

        # Note: follow_redirects=True is mandatory.
        # The NBI REST API lives on port 8443. Accessing it without a valid
        # session redirects to CAS (on port 8843). We use the initial redirect
        # URL to obtain the correctly scoped execution token.
        self._http_client = httpx.Client(
            verify=False,  # Self-signed cert in lab — MVP acceptable
            timeout=15.0,
            follow_redirects=True,
        )
        self._authenticate_cas(username, password)

    def _authenticate_cas(self, username: str, password: str) -> None:
        """Perform CAS SSO login to obtain a session cookie.

        The SM Optics ONC NBI lives on port 8443. Accessing any protected
        endpoint without a session triggers a redirect to the CAS server
        (port 8843 internally). The correct CAS execution token is scoped
        to the 8443 service URL, so we bootstrap authentication by:

        1. GET /onc/nbi/ne on port 8443 → follows redirect to CAS login page.
        2. Parse the execution token from the CAS form (already scoped correctly).
        3. POST credentials to the CAS URL from step 1.
        4. CAS redirects back to /onc/login/cas which sets the session cookie.

        The httpx client's cookie jar persists the session across all
        subsequent API calls.

        Args:
            username: CAS username.
            password: CAS password.

        Raises:
            RuntimeError: If the CAS execution token cannot be found in the form.
            httpx.HTTPStatusError: If authentication fails.
        """
        # GET a protected NBI endpoint to trigger the CAS redirect chain
        nbi_probe_url = f"{self._base_url}{self._NBI_PREFIX}/ne"
        resp = self._http_client.get(
            nbi_probe_url, headers={"Accept": "application/json"}
        )

        # If we got JSON directly, session is already valid (cookie reuse)
        ct = resp.headers.get("content-type", "")
        if "application/json" in ct:
            logger.info("CAS session already valid for %s.", self._base_url)
            return

        # Parse execution token from the CAS login form
        execution_match = re.search(
            r'name="execution"\s+value="([^"]+)"', resp.text
        )
        if not execution_match:
            msg = (
                "Cannot find CAS 'execution' token. "
                "CAS form not found in response from %s. "
                "Check base_url and network connectivity."
            ) % resp.url
            raise RuntimeError(msg)

        execution_token = execution_match.group(1)
        cas_login_url = str(resp.url)  # The actual CAS URL after redirect

        # POST credentials to the CAS endpoint (scoped to the 8443 service)
        login_payload = {
            "username": username,
            "password": password,
            "execution": execution_token,
            "_eventId": "submit",
            "geolocation": "",
        }
        resp = self._http_client.post(cas_login_url, data=login_payload)
        resp.raise_for_status()

        logger.info(
            "CAS authentication successful. Session established for %s.",
            self._base_url,
        )

    @property
    def base_url(self) -> str:
        """The controller base URL."""
        return self._base_url

    @property
    def ne_filter(self) -> str:
        """The keyword used to filter NEs by name."""
        return self._ne_filter

    def health_check(self) -> bool:
        """Check if the ONC controller is reachable.

        Makes a lightweight GET /ne request. Returns True if the controller
        responds with 2xx, False on connection or HTTP errors.

        Returns:
            True if testbed is reachable and responsive, False otherwise.
        """
        try:
            response = self._http_client.get(
                f"{self._base_url}{self._NBI_PREFIX}/ne",
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return True
        except (httpx.ConnectError, httpx.TimeoutException):
            logger.warning("ONC health check failed: connection error.")
            return False
        except httpx.HTTPStatusError as exc:
            logger.warning("ONC health check failed: HTTP %s.", exc.response.status_code)
            return False

    def get_network_elements(self) -> list[dict]:
        """Fetch and filter Network Elements from the ONC controller.

        Calls GET /ne and returns only NEs whose name contains ne_filter.
        This isolates the 'Qiaolun' topology from the other topology
        coexisting in the same controller environment.

        Returns:
            List of NE dicts from NeListGetResponse, filtered by ne_filter.

        Raises:
            httpx.HTTPStatusError: On non-2xx HTTP responses.
            httpx.ConnectError: If the controller is unreachable.
        """
        response = self._http_client.get(
            f"{self._base_url}{self._NBI_PREFIX}/ne",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        all_nes: list[dict] = response.json()
        return [ne for ne in all_nes if self._ne_filter in ne.get("name", "")]

    def get_connections(self, connection_type: str = "infrastructure-eth") -> list[dict]:
        """Fetch connection inventory from the ONC controller.

        Calls GET /connection with the specified connectionType filter.
        For topology discovery, use 'infrastructure-eth' to get the
        physical infrastructure links between NEs.

        Args:
            connection_type: The ONC connectionType query parameter.
                Valid values: 'infrastructure-eth', 'infrastructure-eth-nni',
                'service-evc', etc. (see onc-nbi.yaml).

        Returns:
            List of connection dicts from ConnectionListGetResponse.

        Raises:
            httpx.HTTPStatusError: On non-2xx HTTP responses.
            httpx.ConnectError: If the controller is unreachable.
        """
        try:
            response = self._http_client.get(
                f"{self._base_url}{self._NBI_PREFIX}/connection",
                params={"connectionType": connection_type},
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            # The SM Optics ONC returns 400 "Connection not Found" when no
            # connections of the requested type exist (instead of 200 []).
            # We treat this as an empty list to keep the caller simple.
            if exc.response.status_code == 400:
                logger.debug(
                    "No connections of type '%s' found (ONC returned 400). "
                    "Treating as empty list.",
                    connection_type,
                )
                return []
            raise

    def get_topology(self) -> TopologySnapshot:
        """Assemble a TopologySnapshot from live ONC NBI data.

        Orchestrates get_network_elements() and get_connections() to build
        a structured topology. Maps ONC NE objects → NetworkNode and
        derives FiberLink adjacency from connection endpoints.

        Physical parameters (length_km, num_amplifiers) come from
        link_physics config or fall back to ECOC-realistic defaults.

        Returns:
            A TopologySnapshot with nodes and links from the Qiaolun topology.

        Raises:
            httpx.HTTPStatusError: On non-2xx HTTP responses.
            httpx.ConnectError: If the controller is unreachable.
        """
        nes = self.get_network_elements()
        connections = self.get_connections("infrastructure-eth")

        # Build NetworkNode objects
        ne_name_to_id: dict[str, str] = {}
        nodes: list[NetworkNode] = []
        for i, ne in enumerate(nes):
            node_id = f"ne_{i}"
            ne_name = ne.get("name", f"NE-{i}")
            ne_name_to_id[ne_name] = node_id
            nodes.append(
                NetworkNode(
                    node_id=node_id,
                    name=ne_name,
                    interfaces=[],
                )
            )

        # Build FiberLink objects from connection endpoints
        links: list[FiberLink] = []
        for i, conn in enumerate(connections):
            endpoints = conn.get("connEndPoints", [])
            ne_names_in_conn = [
                ep.get("ltp", {}).get("ne", {}).get("name", "")
                for ep in endpoints
                if ep.get("ltp", {}).get("ne", {}).get("name")
            ]

            if len(ne_names_in_conn) < 2:
                continue  # Skip connections without two identifiable NE endpoints

            src_name, dst_name = ne_names_in_conn[0], ne_names_in_conn[1]
            src_id = ne_name_to_id.get(src_name)
            dst_id = ne_name_to_id.get(dst_name)

            if src_id is None or dst_id is None:
                # Connection references NEs outside the filtered topology
                continue

            conn_name = conn.get("name", f"link_{i}")
            physics = self._link_physics.get(conn_name, self._link_physics.get("default", {}))

            links.append(
                FiberLink(
                    link_id=conn_name,
                    source_node=src_id,
                    target_node=dst_id,
                    length_km=physics.get("length_km", 25.0),
                    num_amplifiers=physics.get("num_amplifiers", 1),
                    active_channels=physics.get("active_channels", 4),
                )
            )

        return TopologySnapshot(
            nodes=nodes,
            links=links,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http_client.close()

    def __enter__(self) -> RESTConfTestbedClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
