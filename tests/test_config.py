"""
Tests for COGNEE-jart-on configuration module.
"""

import os

import pytest

from cognee_jart_on.config import (
    CogneeConfig,
    DatabaseConfig,
    LiteLLMConfig,
    OllamaEmbeddingConfig,
)

pytestmark = pytest.mark.unit


class TestLiteLLMConfig:
    def test_default_values(self):
        config = LiteLLMConfig()
        assert config.base_url == "http://localhost:4000"
        assert config.api_key == "sk-litellm"
        assert config.model == "cognee-llm"

    def test_as_env(self):
        config = LiteLLMConfig()
        env = config.as_env()
        assert env["LLM_PROVIDER"] == "custom"
        assert env["LLM_MODEL"] == "custom/cognee-llm"  # custom/ prefix for LiteLLM
        assert "localhost:4000" in env["LLM_ENDPOINT"]
        assert env["LLM_API_KEY"] == "sk-litellm"


class TestOllamaEmbeddingConfig:
    def test_default_values(self):
        config = OllamaEmbeddingConfig()
        assert config.base_url == "http://localhost:11434"
        assert config.model == "nomic-embed-text:latest"
        assert config.dimensions == 768

    def test_as_env(self):
        config = OllamaEmbeddingConfig()
        env = config.as_env()
        assert env["EMBEDDING_PROVIDER"] == "ollama"
        assert "localhost:11434" in env["EMBEDDING_ENDPOINT"]
        assert env["EMBEDDING_DIMENSIONS"] == "768"


class TestDatabaseConfig:
    def test_default_local(self):
        config = DatabaseConfig()
        assert config.db_provider == "sqlite"
        assert config.graph_provider == "kuzu"
        assert config.vector_provider == "lancedb"

    def test_as_env_postgres(self):
        config = DatabaseConfig(
            db_provider="postgres",
            db_host="192.168.1.100",
        )
        env = config.as_env()
        assert env["DB_PROVIDER"] == "postgres"
        assert env["DB_HOST"] == "192.168.1.100"

    def test_as_env_pgvector_reuses_postgres(self):
        """pgvector must point at the shared Postgres, not a separate service."""
        config = DatabaseConfig(
            db_provider="postgres",
            db_host="10.0.0.5",
            db_password="secret",
            vector_provider="pgvector",
        )
        env = config.as_env()
        assert env["VECTOR_DB_PROVIDER"] == "pgvector"
        assert env["VECTOR_DB_HOST"] == "10.0.0.5"
        assert env["VECTOR_DB_PASSWORD"] == "secret"
        assert env["VECTOR_DB_NAME"] == config.db_name


class TestCogneeConfig:
    def test_local_dev(self):
        config = CogneeConfig.local_dev()
        assert config.database.db_provider == "sqlite"
        assert "localhost:4000" in config.litellm.base_url
        assert "localhost:11434" in config.embeddings.base_url

    def test_p2p_shared(self):
        config = CogneeConfig.p2p_shared(
            litellm_host="192.168.1.100",
            db_host="192.168.1.100",
        )
        assert config.database.db_provider == "postgres"
        assert "192.168.1.100" in config.litellm.base_url
        assert config.database.graph_provider == "neo4j"
        assert config.database.vector_provider == "pgvector"

    def test_apply_env(self):
        config = CogneeConfig.local_dev()
        config.apply_env()

        assert os.environ["LLM_PROVIDER"] == "custom"
        assert os.environ["EMBEDDING_PROVIDER"] == "ollama"
        assert os.environ["STRUCTURED_OUTPUT_FRAMEWORK"] == "instructor"
        assert os.environ["REQUIRE_AUTHENTICATION"] == "false"
        assert os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] == "false"

    def test_from_env(self):
        saved = {
            "LITELLM_BASE_URL": os.environ.get("LITELLM_BASE_URL"),
            "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL"),
        }
        try:
            os.environ["LITELLM_BASE_URL"] = "http://test:4000"
            os.environ["OLLAMA_BASE_URL"] = "http://test:11434"

            config = CogneeConfig.from_env()
            assert config.litellm.base_url == "http://test:4000"
            assert config.embeddings.base_url == "http://test:11434"
        finally:
            for key, val in saved.items():
                if val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = val
    def test_revert_env_restores_originals(self):
        """revert_env() should undo all mutations from apply_env()."""
        config = CogneeConfig.local_dev()
        # Capture original state
        orig_keys = [
            "LLM_PROVIDER", "EMBEDDING_PROVIDER", "STRUCTURED_OUTPUT_FRAMEWORK",
            "REQUIRE_AUTHENTICATION", "FASTAPI_USERS_JWT_SECRET",
        ]
        originals = {k: os.environ.get(k) for k in orig_keys}
        try:
            config.apply_env()
            assert os.environ.get("LLM_PROVIDER") == "custom"
            config.revert_env()
            for k in orig_keys:
                assert os.environ.get(k) == originals[k], f"{k} not reverted"
        finally:
            # Hard cleanup in case assert fails
            for k, v in originals.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_auth_enabled_requires_jwt_secret(self):
        """apply_env() with auth_enabled=True and empty jwt_secret must raise ValueError."""
        config = CogneeConfig(auth_enabled=True, jwt_secret="")
        try:
            with __import__("pytest").raises(ValueError, match="non-empty jwt_secret"):
                config.apply_env()
        finally:
            config.revert_env()

    def test_default_jwt_secret_is_empty(self):
        """Default jwt_secret must be empty to prevent accidental insecure defaults."""
        config = CogneeConfig()
        assert config.jwt_secret == ""

    def test_from_env_reads_graph_credentials(self):
        """from_env() should read GRAPH_DATABASE_USERNAME and GRAPH_DATABASE_PASSWORD."""
        saved = {
            "GRAPH_DATABASE_USERNAME": os.environ.get("GRAPH_DATABASE_USERNAME"),
            "GRAPH_DATABASE_PASSWORD": os.environ.get("GRAPH_DATABASE_PASSWORD"),
        }
        try:
            os.environ["GRAPH_DATABASE_USERNAME"] = "neo4j"
            os.environ["GRAPH_DATABASE_PASSWORD"] = "s3cret"
            config = CogneeConfig.from_env()
            assert config.database.graph_username == "neo4j"
            assert config.database.graph_password == "s3cret"
        finally:
            for key, val in saved.items():
                if val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = val
