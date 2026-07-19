"""
Unit tests for cognee_jart_on.mcp_server.

The MCP Server registers list/call handlers; we invoke them directly with a
faked cognee, so no services are needed. Covers the advertised tool set and
the call_tool dispatch/marshalling/error path.
"""

from __future__ import annotations

import json
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.types import CallToolRequest, CallToolRequestParams, ListToolsRequest

from cognee_jart_on.config import CogneeConfig
from cognee_jart_on.mcp_server import create_mcp_server

pytestmark = pytest.mark.unit


@pytest.fixture
def server():
    return create_mcp_server(CogneeConfig.local_dev())


@pytest.fixture
def fake_cognee(monkeypatch):
    cog = types.ModuleType("cognee")
    cog.remember = AsyncMock(return_value=SimpleNamespace(status="completed"))
    cog.recall = AsyncMock(
        return_value=[SimpleNamespace(text="hello", source="doc1")]
    )
    cog.improve = AsyncMock(return_value=None)
    cog.forget = AsyncMock(return_value="ok")
    cog.datasets = MagicMock()
    cog.datasets.list_datasets = AsyncMock(return_value=[])
    monkeypatch.setitem(sys.modules, "cognee", cog)
    return cog


async def _call(server, name, arguments):
    handler = server.request_handlers[CallToolRequest]
    req = CallToolRequest(
        method="tools/call",
        params=CallToolRequestParams(name=name, arguments=arguments),
    )
    result = await handler(req)
    return json.loads(result.root.content[0].text)


class TestListTools:
    async def test_advertises_expected_tools(self, server):
        handler = server.request_handlers[ListToolsRequest]
        result = await handler(ListToolsRequest(method="tools/list"))
        names = {t.name for t in result.root.tools}
        assert names == {
            "remember", "recall", "improve", "forget",
            "list_datasets", "sync_status",
        }

    async def test_remember_requires_data(self, server):
        handler = server.request_handlers[ListToolsRequest]
        result = await handler(ListToolsRequest(method="tools/list"))
        remember = next(t for t in result.root.tools if t.name == "remember")
        assert remember.inputSchema["required"] == ["data"]


class TestCallTool:
    async def test_remember_dispatches(self, server, fake_cognee):
        out = await _call(server, "remember", {"data": "x", "dataset_name": "ds"})
        fake_cognee.remember.assert_awaited_once()
        assert out["status"] == "completed"
        assert out["dataset_name"] == "ds"

    async def test_recall_parses_csv_datasets(self, server, fake_cognee):
        out = await _call(server, "recall", {"query": "q", "datasets": "a,b"})
        _, kwargs = fake_cognee.recall.await_args
        assert kwargs["datasets"] == ["a", "b"]
        assert out["count"] == 1

    async def test_unknown_tool_returns_error(self, server, fake_cognee):
        out = await _call(server, "does_not_exist", {})
        assert "Unknown tool" in out["error"]

    async def test_exception_is_wrapped(self, server, fake_cognee):
        fake_cognee.remember.side_effect = RuntimeError("kaboom")
        out = await _call(server, "remember", {"data": "x"})
        assert "kaboom" in out["error"]
