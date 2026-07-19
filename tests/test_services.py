"""
Tests for service health and connectivity.
Verifies all external services are reachable and responding.
"""

import json

import pytest
import urllib.request
import urllib.error


def _http_get(url: str, headers: dict = None, timeout: int = 5) -> tuple:
    """Simple HTTP GET helper."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)


def _http_post(url: str, data: dict, headers: dict = None, timeout: int = 10) -> tuple:
    """Simple HTTP POST helper."""
    body = json.dumps(data).encode()
    h = {"Content-Type": "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)


class TestServiceHealth:
    """Test that all Docker services are healthy and responding."""

    def test_postgres_running(self):
        """PostgreSQL should be accepting connections."""
        import subprocess
        result = subprocess.run(
            ["docker", "inspect", "cognee-postgres", "--format", "{{.State.Health.Status}}"],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        assert status in ("healthy", "starting"), f"Postgres status: {status}"

    def test_neo4j_running(self):
        """Neo4j should respond on bolt port."""
        status, body = _http_get("http://localhost:7474")
        assert status == 200
        data = json.loads(body)
        assert "neo4j_version" in data

    def test_qdrant_healthy(self):
        """Qdrant healthz should pass."""
        status, body = _http_get("http://localhost:6333/healthz")
        assert status == 200

    def test_litellm_healthy(self):
        """LiteLLM should have healthy endpoints."""
        status, body = _http_get(
            "http://localhost:4000/health",
            headers={"Authorization": "Bearer sk-litellm"}
        )
        assert status == 200
        data = json.loads(body)
        assert data["healthy_count"] > 0

    def test_litellm_model_available(self):
        """LiteLLM should expose cognee-llm model."""
        status, body = _http_get(
            "http://localhost:4000/v1/models",
            headers={"Authorization": "Bearer sk-litellm"}
        )
        assert status == 200
        data = json.loads(body)
        models = [m["id"] for m in data.get("data", [])]
        assert "cognee-llm" in models

    def test_ollama_running(self):
        """Ollama should be reachable and have embedding model."""
        status, body = _http_get("http://localhost:11434/api/tags")
        assert status == 200
        data = json.loads(body)
        models = [m["name"] for m in data.get("models", [])]
        assert any("nomic-embed-text" in m for m in models), f"Missing nomic-embed-text, have: {models}"


class TestLiteLLMIntegration:
    """Test LiteLLM proxy can make real LLM calls."""

    def test_chat_completion(self):
        """LiteLLM should return a valid chat completion."""
        status, body = _http_post(
            "http://localhost:4000/v1/chat/completions",
            {
                "model": "cognee-llm",
                "messages": [{"role": "user", "content": "Say hello in 3 words."}],
                "max_tokens": 20,
            },
            headers={"Authorization": "Bearer sk-litellm"},
        )
        assert status == 200
        data = json.loads(body)
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert data["choices"][0]["message"]["content"]

    def test_structured_output(self):
        """LiteLLM should handle JSON structured output."""
        status, body = _http_post(
            "http://localhost:4000/v1/chat/completions",
            {
                "model": "cognee-llm",
                "messages": [{"role": "user", "content": 'Return JSON: {"name": "test", "value": 42}'}],
                "response_format": {"type": "json_object"},
                "max_tokens": 50,
            },
            headers={"Authorization": "Bearer sk-litellm"},
        )
        assert status == 200
        data = json.loads(body)
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        assert "name" in parsed or "value" in parsed

    def test_litellm_tracks_spend(self):
        """LiteLLM should return cost in response headers."""
        req = urllib.request.Request(
            "http://localhost:4000/v1/chat/completions",
            data=json.dumps({
                "model": "cognee-llm",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-litellm",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            cost_header = resp.headers.get("x-litellm-response-cost")
            assert cost_header is not None, "Missing x-litellm-response-cost header"
            cost = float(cost_header)
            assert cost >= 0


class TestOllamaEmbeddings:
    """Test Ollama embedding service."""

    def test_embedding_generation(self):
        """Ollama should generate embeddings from nomic-embed-text."""
        status, body = _http_post(
            "http://localhost:11434/api/embed",
            {
                "model": "nomic-embed-text:latest",
                "input": "test embedding",
            },
        )
        assert status == 200
        data = json.loads(body)
        assert "embeddings" in data
        assert len(data["embeddings"]) > 0
        assert len(data["embeddings"][0]) == 768, f"Expected 768 dims, got {len(data['embeddings'][0])}"


class TestCogneeIntegration:
    """Test Cognee can bootstrap and use the services."""

    @pytest.fixture
    def config(self):
        from cognee_jart_on.config import CogneeConfig
        return CogneeConfig.local_dev()

    def test_config_applies_env(self, config):
        """Config should set all required env vars."""
        config.apply_env()
        import os
        assert os.environ["LLM_PROVIDER"] == "custom"
        assert os.environ["EMBEDDING_PROVIDER"] == "ollama"
        assert os.environ["STRUCTURED_OUTPUT_FRAMEWORK"] == "instructor"
