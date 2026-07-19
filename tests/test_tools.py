"""
Unit tests for cognee_jart_on.tools.

Cognee is replaced with an in-memory fake, so these run with no services:
they verify argument marshalling, dataset CSV parsing, JSON shaping and
error handling — the logic this package actually owns.
"""

from __future__ import annotations

import json
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from cognee_jart_on import tools

pytestmark = pytest.mark.unit


@pytest.fixture
def fake_cognee(monkeypatch):
    """Install a fake `cognee` module and hand it back for assertions."""
    cog = types.ModuleType("cognee")
    cog.remember = AsyncMock(return_value=SimpleNamespace(status="completed"))
    cog.recall = AsyncMock(
        return_value=[
            SimpleNamespace(text="Einstein was born in Ulm.", source="doc1"),
        ]
    )
    cog.improve = AsyncMock(return_value=SimpleNamespace(status="completed"))
    cog.forget = AsyncMock(return_value="deleted")
    cog.datasets = MagicMock()
    cog.datasets.list_datasets = AsyncMock(
        return_value=[SimpleNamespace(id="id-1", name="main_dataset")]
    )
    monkeypatch.setitem(sys.modules, "cognee", cog)
    return cog


class TestRemember:
    async def test_forwards_arguments(self, fake_cognee):
        out = json.loads(await tools.remember("hi", dataset_name="ds", session_id="s1"))
        fake_cognee.remember.assert_awaited_once_with(
            data="hi", dataset_name="ds", session_id="s1"
        )
        assert out["status"] == "completed"
        assert out["dataset_name"] == "ds"
        assert out["session_id"] == "s1"

    async def test_reports_errors_as_json(self, fake_cognee):
        fake_cognee.remember.side_effect = RuntimeError("boom")
        out = json.loads(await tools.remember("hi"))
        assert out["status"] == "error"
        assert "boom" in out["error"]


class TestRecall:
    async def test_parses_csv_datasets_and_shapes_results(self, fake_cognee):
        out = json.loads(await tools.recall("q", datasets="a, b ,c", top_k=3))
        _, kwargs = fake_cognee.recall.await_args
        assert kwargs["datasets"] == ["a", "b", "c"]  # trimmed, split on comma
        assert kwargs["query_text"] == "q"
        assert kwargs["top_k"] == 3
        assert out["count"] == 1
        assert out["results"][0]["text"] == "Einstein was born in Ulm."
        assert out["results"][0]["source"] == "doc1"

    async def test_omits_datasets_when_not_given(self, fake_cognee):
        await tools.recall("q")
        _, kwargs = fake_cognee.recall.await_args
        assert "datasets" not in kwargs

    async def test_reports_errors_as_json(self, fake_cognee):
        fake_cognee.recall.side_effect = ValueError("bad query")
        out = json.loads(await tools.recall("q"))
        assert out["status"] == "error"


class TestImproveForgetList:
    async def test_improve_parses_session_ids(self, fake_cognee):
        await tools.improve(dataset_name="ds", session_ids="s1, s2")
        _, kwargs = fake_cognee.improve.await_args
        assert kwargs["dataset"] == "ds"
        assert kwargs["session_ids"] == ["s1", "s2"]

    async def test_forget_everything_flag(self, fake_cognee):
        await tools.forget(everything=True)
        _, kwargs = fake_cognee.forget.await_args
        assert kwargs["everything"] is True

    async def test_list_datasets_shapes_output(self, fake_cognee):
        out = json.loads(await tools.list_datasets())
        assert out["count"] == 1
        assert out["datasets"][0]["name"] == "main_dataset"


class TestCogneeTools:
    def test_returns_all_tools_without_session(self):
        result = tools.cognee_tools()
        assert len(result) == 5

    async def test_session_injected_only_into_aware_tools(self, fake_cognee):
        wrapped = tools.cognee_tools(session_id="sess-42")
        # First two are session-wrapped remember/recall; the rest are raw.
        await wrapped[0]("hi")
        _, kwargs = fake_cognee.remember.await_args
        assert kwargs["session_id"] == "sess-42"
        # forget must remain the untouched original (no session_id kwarg support)
        assert wrapped[3] is tools.forget

    async def test_explicit_session_overrides_default(self, fake_cognee):
        wrapped = tools.cognee_tools(session_id="default")
        await wrapped[0]("hi", session_id="explicit")
        _, kwargs = fake_cognee.remember.await_args
        assert kwargs["session_id"] == "explicit"
