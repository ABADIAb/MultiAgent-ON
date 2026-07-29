"""Unit tests for the RESTConfTestbedClient (ONC NBI integration).

All HTTP calls are mocked with pytest-mock — no real network required.
Tests validate parsing of ONC NBI responses into our domain models.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.core.state import TopologySnapshot


# ---------------------------------------------------------------------------
# Fixtures: Realistic ONC NBI response payloads
# ---------------------------------------------------------------------------


@pytest.fixture
def ne_response_payload() -> list[dict]:
    """Realistic NeListGetResponse with 3 Qiaolun NEs and 1 other topology NE."""
    return [
        {
            "name": "Qiaolun-NE-01",
            "neType": "1830ONEA",
            "reachability": "connected",
            "operationalState": "enabled",
            "neAddress": {"gui": "10.79.26.50", "mng": "10.79.26.50"},
        },
        {
            "name": "Qiaolun-NE-02",
            "neType": "1830ONEA",
            "reachability": "connected",
            "operationalState": "enabled",
            "neAddress": {"gui": "10.79.26.51", "mng": "10.79.26.51"},
        },
        {
            "name": "Qiaolun-NE-03",
            "neType": "1830ONEA",
            "reachability": "connected",
            "operationalState": "enabled",
            "neAddress": {"gui": "10.79.26.52", "mng": "10.79.26.52"},
        },
        {
            "name": "OtherTopology-NE-01",  # Should be filtered out
            "neType": "LM1",
            "reachability": "connected",
            "operationalState": "enabled",
            "neAddress": {"gui": "10.79.26.60", "mng": "10.79.26.60"},
        },
    ]


@pytest.fixture
def connection_response_payload() -> list[dict]:
    """Realistic ConnectionListGetResponse with infrastructure ETH connections."""
    return [
        {
            "name": "Qiaolun-Link-01-02",
            "hierarchicalLevel": "infrastructure",
            "configurationState": "implemented",
            "operationalState": "enabled",
            "connEndPoints": [
                {"legNumber": 1, "endType": "source", "ltp": {"name": "port-1", "ne": {"name": "Qiaolun-NE-01"}}},
                {"legNumber": 2, "endType": "sink", "ltp": {"name": "port-2", "ne": {"name": "Qiaolun-NE-02"}}},
            ],
        },
        {
            "name": "Qiaolun-Link-02-03",
            "hierarchicalLevel": "infrastructure",
            "configurationState": "implemented",
            "operationalState": "enabled",
            "connEndPoints": [
                {"legNumber": 1, "endType": "source", "ltp": {"name": "port-3", "ne": {"name": "Qiaolun-NE-02"}}},
                {"legNumber": 2, "endType": "sink", "ltp": {"name": "port-4", "ne": {"name": "Qiaolun-NE-03"}}},
            ],
        },
    ]


def _make_mock_response(payload: object, status_code: int = 200) -> MagicMock:
    """Create a mock httpx.Response with JSON payload."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock


def _make_error_response(status_code: int) -> MagicMock:
    """Create a mock httpx.Response that raises HTTPStatusError."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}", request=MagicMock(), response=mock
    )
    return mock


# ---------------------------------------------------------------------------
# Tests: RESTConfTestbedClient construction
# ---------------------------------------------------------------------------


class TestRESTConfTestbedClientConstruction:
    """Validate client initialization."""

    def test_client_stores_base_url(self) -> None:
        from src.services.testbed_client import RESTConfTestbedClient

        with patch("src.services.testbed_client.RESTConfTestbedClient._authenticate_cas"):
            client = RESTConfTestbedClient(
                base_url="https://10.79.26.48", username="admin", password="admin"
            )
        assert "10.79.26.48" in client.base_url

    def test_client_default_ne_filter_is_qiaolun(self) -> None:
        from src.services.testbed_client import RESTConfTestbedClient

        with patch("src.services.testbed_client.RESTConfTestbedClient._authenticate_cas"):
            client = RESTConfTestbedClient(
                base_url="https://10.79.26.48", username="admin", password="admin"
            )
        assert client.ne_filter == "Qiaolun"

    def test_client_accepts_custom_ne_filter(self) -> None:
        from src.services.testbed_client import RESTConfTestbedClient

        with patch("src.services.testbed_client.RESTConfTestbedClient._authenticate_cas"):
            client = RESTConfTestbedClient(
                base_url="https://10.79.26.48",
                username="admin",
                password="admin",
                ne_filter="Custom",
            )
        assert client.ne_filter == "Custom"


# ---------------------------------------------------------------------------
# Tests: health_check
# ---------------------------------------------------------------------------


@pytest.fixture
def onc_client():
    """Provide a RESTConfTestbedClient with CAS auth mocked out."""
    from src.services.testbed_client import RESTConfTestbedClient
    import warnings

    with patch("src.services.testbed_client.RESTConfTestbedClient._authenticate_cas"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            client = RESTConfTestbedClient(
                base_url="https://10.79.26.48", username="admin", password="admin"
            )
    return client


class TestHealthCheck:
    """Validate health check behavior."""

    def test_health_check_returns_true_on_200(
        self, ne_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(ne_response_payload)
            assert onc_client.health_check() is True

    def test_health_check_returns_false_on_connection_error(self, onc_client) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")
            assert onc_client.health_check() is False

    def test_health_check_returns_false_on_http_error(self, onc_client) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_error_response(401)
            assert onc_client.health_check() is False


# ---------------------------------------------------------------------------
# Tests: get_network_elements
# ---------------------------------------------------------------------------


class TestGetNetworkElements:
    """Validate NE fetching and filtering."""

    def test_returns_list_of_dicts(
        self, ne_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(ne_response_payload)
            result = onc_client.get_network_elements()
        assert isinstance(result, list)

    def test_filters_by_qiaolun_keyword(
        self, ne_response_payload: list[dict], onc_client
    ) -> None:
        """Only NEs with 'Qiaolun' in their name should be returned."""
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(ne_response_payload)
            result = onc_client.get_network_elements()
        # 3 Qiaolun NEs, 1 OtherTopology NE — only 3 should pass
        assert len(result) == 3
        for ne in result:
            assert "Qiaolun" in ne["name"]

    def test_ne_payload_contains_name_field(
        self, ne_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(ne_response_payload)
            result = onc_client.get_network_elements()
        for ne in result:
            assert "name" in ne

    def test_calls_ne_endpoint(
        self, ne_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(ne_response_payload)
            onc_client.get_network_elements()
        call_args = mock_get.call_args
        assert "/ne" in str(call_args)


# ---------------------------------------------------------------------------
# Tests: get_connections
# ---------------------------------------------------------------------------


class TestGetConnections:
    """Validate connection fetching."""

    def test_returns_list_of_connections(
        self, connection_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(connection_response_payload)
            result = onc_client.get_connections("infrastructure-eth")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_connection_type_passed_as_query_param(
        self, connection_response_payload: list[dict], onc_client
    ) -> None:
        with patch.object(onc_client._http_client, "get") as mock_get:
            mock_get.return_value = _make_mock_response(connection_response_payload)
            onc_client.get_connections("infrastructure-eth")
        call_kwargs = mock_get.call_args
        assert "infrastructure-eth" in str(call_kwargs)


# ---------------------------------------------------------------------------
# Tests: get_topology
# ---------------------------------------------------------------------------


class TestGetTopology:
    """Validate full topology assembly from NE + connection data."""

    def test_returns_topology_snapshot(
        self,
        ne_response_payload: list[dict],
        connection_response_payload: list[dict],
        onc_client,
    ) -> None:
        with patch.object(onc_client, "get_network_elements") as mock_ne, \
             patch.object(onc_client, "get_connections") as mock_conn:
            mock_ne.return_value = [
                ne for ne in ne_response_payload if "Qiaolun" in ne["name"]
            ]
            mock_conn.return_value = connection_response_payload
            result = onc_client.get_topology()

        assert isinstance(result, TopologySnapshot)

    def test_topology_has_three_nodes(
        self,
        ne_response_payload: list[dict],
        connection_response_payload: list[dict],
        onc_client,
    ) -> None:
        with patch.object(onc_client, "get_network_elements") as mock_ne, \
             patch.object(onc_client, "get_connections") as mock_conn:
            mock_ne.return_value = [
                ne for ne in ne_response_payload if "Qiaolun" in ne["name"]
            ]
            mock_conn.return_value = connection_response_payload
            result = onc_client.get_topology()

        assert len(result.nodes) == 3

    def test_topology_maps_ne_to_network_nodes(
        self,
        ne_response_payload: list[dict],
        connection_response_payload: list[dict],
        onc_client,
    ) -> None:
        with patch.object(onc_client, "get_network_elements") as mock_ne, \
             patch.object(onc_client, "get_connections") as mock_conn:
            mock_ne.return_value = [
                ne for ne in ne_response_payload if "Qiaolun" in ne["name"]
            ]
            mock_conn.return_value = connection_response_payload
            result = onc_client.get_topology()

        node_names = [n.name for n in result.nodes]
        assert "Qiaolun-NE-01" in node_names
        assert "Qiaolun-NE-02" in node_names
        assert "Qiaolun-NE-03" in node_names

    def test_topology_derives_links_from_connections(
        self,
        ne_response_payload: list[dict],
        connection_response_payload: list[dict],
        onc_client,
    ) -> None:
        with patch.object(onc_client, "get_network_elements") as mock_ne, \
             patch.object(onc_client, "get_connections") as mock_conn:
            mock_ne.return_value = [
                ne for ne in ne_response_payload if "Qiaolun" in ne["name"]
            ]
            mock_conn.return_value = connection_response_payload
            result = onc_client.get_topology()

        assert len(result.links) == 2

    def test_topology_timestamp_is_set(
        self,
        ne_response_payload: list[dict],
        connection_response_payload: list[dict],
        onc_client,
    ) -> None:
        with patch.object(onc_client, "get_network_elements") as mock_ne, \
             patch.object(onc_client, "get_connections") as mock_conn:
            mock_ne.return_value = [
                ne for ne in ne_response_payload if "Qiaolun" in ne["name"]
            ]
            mock_conn.return_value = connection_response_payload
            result = onc_client.get_topology()

        assert result.timestamp != ""
