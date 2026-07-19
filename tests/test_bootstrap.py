"""
Unit tests for cognee_jart_on.bootstrap.

Network and cognee are faked, so these run without any live service. They
cover the branching in verify_connections() (local providers report OK
without a socket; unreachable HTTP services report False with an error)
and that setup_cognee() applies env and pushes config into cognee.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit


class _FailingGet:
    """Async context manager whose entry raises, as if the host were down."""

    async def __aenter__(self):
        raise ConnectionError("no network in unit test")

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, *args, **kwargs):
        return _FailingGet()


class TestVerifyConnections:
    async def test_local_providers_ok_without_network(self, monkeypatch):
        import aiohttp

        monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _FakeSession())

        from cognee_jart_on.bootstrap import verify_connections
        from cognee_jart_on.config import CogneeConfig

        results = await verify_connections(CogneeConfig.local_dev())

        # sqlite / kuzu / lancedb need no socket -> always available
        assert results["database"] is True
        assert results["graph"] is True
        assert results["vector"] is True
        # litellm / ollama are HTTP -> unreachable here, reported with an error
        assert results["litellm"] is False
        assert results["ollama"] is False
        assert "litellm_error" in results


class TestSetupCognee:
    async def test_applies_env_and_configures_cognee(self, monkeypatch):
        cog = types.ModuleType("cognee")
        cog.config = MagicMock()
        monkeypatch.setitem(sys.modules, "cognee", cog)

        from cognee_jart_on.bootstrap import setup_cognee
        from cognee_jart_on.config import CogneeConfig

        config = CogneeConfig.local_dev()
        try:
            await setup_cognee(config)
            import os

            assert os.environ["LLM_PROVIDER"] == "custom"
            assert os.environ["EMBEDDING_PROVIDER"] == "ollama"
            cog.config.set_llm_config.assert_called_once()
            cog.config.set_embedding_config.assert_called_once()
        finally:
            config.revert_env()
