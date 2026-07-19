"""
Shared pytest fixtures and service-aware skipping.

Integration/e2e tests are marked at module level. This conftest probes the
required services once per session and skips those tests when the services
are unreachable, so `pytest` runs cleanly on a machine (or CI runner) with
no Docker/Ollama, while still exercising the real pipeline where available.
"""

from __future__ import annotations

import socket

import pytest

# Host:port each marker depends on. A marker is "available" only when every
# endpoint it lists is accepting TCP connections.
_MARKER_ENDPOINTS: dict[str, list[tuple[str, int]]] = {
    "integration": [
        ("localhost", 4000),   # litellm
        ("localhost", 11434),  # ollama
        ("localhost", 5432),   # postgres (relational + pgvector)
        ("localhost", 7474),   # neo4j http
    ],
    "e2e": [
        ("localhost", 4000),   # litellm
        ("localhost", 11434),  # ollama
    ],
}


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Return True if a TCP connection to host:port succeeds."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _marker_available(marker: str, cache: dict[str, bool]) -> bool:
    """Whether every endpoint a marker needs is reachable (memoised)."""
    if marker not in cache:
        endpoints = _MARKER_ENDPOINTS.get(marker, [])
        cache[marker] = all(_port_open(h, p) for h, p in endpoints)
    return cache[marker]


def pytest_collection_modifyitems(config, items):
    """Skip integration/e2e items whose services are down."""
    availability: dict[str, bool] = {}
    for item in items:
        for marker in _MARKER_ENDPOINTS:
            if marker in item.keywords and not _marker_available(marker, availability):
                item.add_marker(
                    pytest.mark.skip(
                        reason=f"'{marker}' services unreachable — skipping"
                    )
                )
