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


class MockTestbedClient(TestbedClient):
    """Mock testbed client returning realistic ECOC 4-node topology.

    Based on the ECOC 2024 paper's testbed at Politecnico di Milano:
    4 nodes in a linear topology with fiber spans and OAs.
    """

    def get_topology(self) -> TopologySnapshot:
        """Return a hardcoded but realistic 4-node linear topology."""
        nodes = [
            NetworkNode(
                node_id="node_1",
                name="Milano-A",
                interfaces=[101, 102],
            ),
            NetworkNode(
                node_id="node_2",
                name="Milano-B",
                interfaces=[201, 202, 203, 204],
            ),
            NetworkNode(
                node_id="node_3",
                name="Milano-C",
                interfaces=[301, 302, 303, 304],
            ),
            NetworkNode(
                node_id="node_4",
                name="Milano-D",
                interfaces=[401, 402],
            ),
        ]

        links = [
            FiberLink(
                link_id="link_ab",
                source_node="node_1",
                target_node="node_2",
                length_km=20.0,
                num_amplifiers=1,
                active_channels=4,
            ),
            FiberLink(
                link_id="link_bc",
                source_node="node_2",
                target_node="node_3",
                length_km=40.0,
                num_amplifiers=2,
                active_channels=6,
            ),
            FiberLink(
                link_id="link_cd",
                source_node="node_3",
                target_node="node_4",
                length_km=30.0,
                num_amplifiers=1,
                active_channels=2,
            ),
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
