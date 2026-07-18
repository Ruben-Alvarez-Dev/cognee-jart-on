"""
Tests for COGNEE-jart-on configuration module.
"""

import os

from cognee_jart_on.config import (
    CogneeConfig,
    DatabaseConfig,
    LiteLLMConfig,
    OllamaEmbeddingConfig,
)


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

    def test_apply_env(self):
        config = CogneeConfig.local_dev()
        config.apply_env()

        assert os.environ["LLM_PROVIDER"] == "custom"
        assert os.environ["EMBEDDING_PROVIDER"] == "ollama"
        assert os.environ["STRUCTURED_OUTPUT_FRAMEWORK"] == "instructor"
        assert os.environ["REQUIRE_AUTHENTICATION"] == "false"
        assert os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] == "false"

    def test_from_env(self):
        os.environ["LITELLM_BASE_URL"] = "http://test:4000"
        os.environ["OLLAMA_BASE_URL"] = "http://test:11434"

        config = CogneeConfig.from_env()
        assert config.litellm.base_url == "http://test:4000"
        assert config.embeddings.base_url == "http://test:11434"

        # Cleanup
        del os.environ["LITELLM_BASE_URL"]
        del os.environ["OLLAMA_BASE_URL"]
