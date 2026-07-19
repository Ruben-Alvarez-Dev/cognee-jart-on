"""
Unit tests for cognee_jart_on.cli.

verify_connections is faked, so the CLI is exercised end-to-end (option
parsing, config assembly, exit codes, output) without touching a network.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from cognee_jart_on.cli import cli

pytestmark = pytest.mark.unit


def _fake_verify(results, sink=None):
    """Build an async stand-in for verify_connections capturing its config."""

    async def _verify(config):
        if sink is not None:
            sink["config"] = config
        return results

    return _verify


_ALL_OK = {k: True for k in ("litellm", "ollama", "database", "graph", "vector")}


class TestStatus:
    def test_reports_each_service(self, monkeypatch):
        monkeypatch.setattr(
            "cognee_jart_on.bootstrap.verify_connections", _fake_verify(_ALL_OK)
        )
        result = CliRunner().invoke(cli, ["status"])
        assert result.exit_code == 0
        for service in ("litellm", "ollama", "database", "graph", "vector"):
            assert service in result.output


class TestInit:
    def test_exit_zero_when_all_ok(self, monkeypatch):
        monkeypatch.setattr(
            "cognee_jart_on.bootstrap.verify_connections", _fake_verify(_ALL_OK)
        )
        result = CliRunner().invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "All services ready" in result.output

    def test_exit_one_when_a_service_fails(self, monkeypatch):
        broken = {**_ALL_OK, "graph": False}
        monkeypatch.setattr(
            "cognee_jart_on.bootstrap.verify_connections", _fake_verify(broken)
        )
        result = CliRunner().invoke(cli, ["init"])
        assert result.exit_code == 1

    def test_shared_db_builds_postgres_config(self, monkeypatch):
        sink: dict = {}
        monkeypatch.setattr(
            "cognee_jart_on.bootstrap.verify_connections",
            _fake_verify(_ALL_OK, sink),
        )
        result = CliRunner().invoke(
            cli, ["init", "--shared-db", "--db-host", "10.0.0.5"]
        )
        assert result.exit_code == 0
        db = sink["config"].database
        assert db.db_provider == "postgres"
        assert db.db_host == "10.0.0.5"
        assert db.graph_provider == "neo4j"
        assert db.vector_provider == "pgvector"

    def test_local_by_default(self, monkeypatch):
        sink: dict = {}
        monkeypatch.setattr(
            "cognee_jart_on.bootstrap.verify_connections",
            _fake_verify(_ALL_OK, sink),
        )
        CliRunner().invoke(cli, ["init"])
        assert sink["config"].database.db_provider == "sqlite"
