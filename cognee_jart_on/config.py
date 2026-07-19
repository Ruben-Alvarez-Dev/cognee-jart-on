"""
Configuration for COGNEE-jart-on.

Defines all settings for the P2P Cognee integration:
- LiteLLM proxy connection (LLM enmascarado)
- Ollama local embeddings
- Shared database backends (Postgres, Neo4j, Qdrant)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LiteLLMConfig:
    """LiteLLM proxy configuration for LLM calls."""

    base_url: str = "http://localhost:4000"
    api_key: str = "sk-litellm"
    model: str = "cognee-llm"
    timeout: int = 120

    def as_env(self) -> dict[str, str]:
        """Return env vars to configure Cognee's LLM to use LiteLLM proxy.

        Cognee routes through LiteLLM internally. For LLM_PROVIDER="custom",
        LiteLLM uses the custom/ prefix. The model name must match what
        LiteLLM proxy exposes in its config.yaml (model_name field).
        """
        return {
            "LLM_PROVIDER": "custom",
            "LLM_MODEL": f"custom/{self.model}",
            "LLM_ENDPOINT": f"{self.base_url}/v1",
            "LLM_API_KEY": self.api_key,
            "LLM_TEMPERATURE": "0.0",
            "LLM_MAX_COMPLETION_TOKENS": "16384",
        }


@dataclass
class OllamaEmbeddingConfig:
    """Ollama local embedding configuration."""

    base_url: str = "http://localhost:11434"
    model: str = "nomic-embed-text:latest"
    dimensions: int = 768
    tokenizer: str = "nomic-ai/nomic-embed-text-v1.5"

    def as_env(self) -> dict[str, str]:
        """Return env vars to configure Cognee's embeddings to use Ollama."""
        return {
            "EMBEDDING_PROVIDER": "ollama",
            "EMBEDDING_MODEL": self.model,
            "EMBEDDING_ENDPOINT": f"{self.base_url}/api/embed",
            "EMBEDDING_DIMENSIONS": str(self.dimensions),
            "HUGGINGFACE_TOKENIZER": self.tokenizer,
        }


@dataclass
class DatabaseConfig:
    """Shared database backend configuration for P2P."""

    # Relational (PostgreSQL shared)
    db_provider: str = "sqlite"
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "cognee"
    db_password: str = "cognee"
    db_name: str = "cognee_db"

    # Graph (Kuzu local by default, Neo4j for shared)
    graph_provider: str = "kuzu"
    graph_url: str = ""
    graph_username: str = ""
    graph_password: str = ""

    # Vector (LanceDB local by default, Qdrant for shared)
    vector_provider: str = "lancedb"
    vector_url: str = ""

    def as_env(self) -> dict[str, str]:
        """Return env vars for database configuration."""
        env = {
            "DB_PROVIDER": self.db_provider,
            "DB_NAME": self.db_name,
            "GRAPH_DATABASE_PROVIDER": self.graph_provider,
            "VECTOR_DB_PROVIDER": self.vector_provider,
        }

        if self.db_provider == "postgres":
            env.update({
                "DB_HOST": self.db_host,
                "DB_PORT": str(self.db_port),
                "DB_USERNAME": self.db_username,
                "DB_PASSWORD": self.db_password,
            })

        if self.graph_provider == "neo4j" and self.graph_url:
            env.update({
                "GRAPH_DATABASE_URL": self.graph_url,
                "GRAPH_DATABASE_USERNAME": self.graph_username,
                "GRAPH_DATABASE_PASSWORD": self.graph_password,
            })

        if self.vector_provider == "qdrant" and self.vector_url:
            env["VECTOR_DB_URL"] = self.vector_url

        return env


@dataclass
class CogneeConfig:
    """Complete configuration for COGNEE-jart-on."""

    litellm: LiteLLMConfig = field(default_factory=LiteLLMConfig)
    embeddings: OllamaEmbeddingConfig = field(default_factory=OllamaEmbeddingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    # Auth
    auth_enabled: bool = False
    jwt_secret: str = ""

    # Data directories
    data_root: Optional[str] = None

    # Track env vars set by apply_env so revert_env() can undo them
    _env_originals: dict[str, Optional[str]] = field(
        default_factory=dict, init=False, repr=False
    )

    def apply_env(self) -> None:
        """Apply all configuration as environment variables.

        Must be called BEFORE importing cognee.
        Stores originals so revert_env() can undo the mutations.
        """
        # Structured output — BAML not needed when LLM is behind LiteLLM
        # (LiteLLM handles provider abstraction, so instructor/json_schema_mode works)
        env_vars: dict[str, str] = {}
        env_vars["STRUCTURED_OUTPUT_FRAMEWORK"] = "instructor"

        # Auth
        if self.auth_enabled and not self.jwt_secret:
            raise ValueError(
                "auth_enabled=True requires a non-empty jwt_secret. "
                "Set jwt_secret explicitly or via FASTAPI_USERS_JWT_SECRET env var."
            )
        env_vars["REQUIRE_AUTHENTICATION"] = str(self.auth_enabled).lower()
        env_vars["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
        env_vars["FASTAPI_USERS_JWT_SECRET"] = self.jwt_secret

        # Disable auto migrations on peer startup (server handles migrations)
        env_vars["ENABLE_AUTO_MIGRATIONS"] = "false"

        # Apply subsystem configs
        for env_dict in [
            self.litellm.as_env(),
            self.embeddings.as_env(),
            self.database.as_env(),
        ]:
            for key, value in env_dict.items():
                env_vars[key] = value

        # Data root
        if self.data_root:
            env_vars["DATA_ROOT_DIRECTORY"] = self.data_root

        # Store originals before overwriting
        self._env_originals = {
            key: os.environ.get(key) for key in env_vars
        }
        os.environ.update(env_vars)

    def revert_env(self) -> None:
        """Undo all environment variable mutations from apply_env().

        Restores original values for keys that existed before apply_env(),
        and deletes keys that didn't exist.
        """
        for key, original in self._env_originals.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original
        self._env_originals = {}

    @classmethod
    def from_env(cls) -> "CogneeConfig":
        """Build config from existing environment variables."""
        return cls(
            litellm=LiteLLMConfig(
                base_url=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
                api_key=os.getenv("LITELLM_API_KEY", "sk-litellm"),
                model=os.getenv("LITELLM_MODEL", "cognee-llm"),
            ),
            embeddings=OllamaEmbeddingConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest"),
                dimensions=int(os.getenv("OLLAMA_EMBEDDING_DIMENSIONS", "768")),
            ),
            database=DatabaseConfig(
                db_provider=os.getenv("DB_PROVIDER", "sqlite"),
                db_host=os.getenv("DB_HOST", "localhost"),
                db_port=int(os.getenv("DB_PORT", "5432")),
                db_username=os.getenv("DB_USERNAME", "cognee"),
                db_password=os.getenv("DB_PASSWORD", "cognee"),
                db_name=os.getenv("DB_NAME", "cognee_db"),
                graph_provider=os.getenv("GRAPH_DATABASE_PROVIDER", "kuzu"),
                graph_url=os.getenv("GRAPH_DATABASE_URL", ""),
                graph_username=os.getenv("GRAPH_DATABASE_USERNAME", ""),
                graph_password=os.getenv("GRAPH_DATABASE_PASSWORD", ""),
                vector_provider=os.getenv("VECTOR_DB_PROVIDER", "lancedb"),
                vector_url=os.getenv("VECTOR_DB_URL", ""),
            ),
            auth_enabled=os.getenv("REQUIRE_AUTHENTICATION", "false").lower() == "true",
            jwt_secret=os.getenv("FASTAPI_USERS_JWT_SECRET", ""),
            data_root=os.getenv("DATA_ROOT_DIRECTORY"),
        )

    @classmethod
    def local_dev(cls) -> "CogneeConfig":
        """Quick config for local development (all local, no shared DBs)."""
        return cls(
            litellm=LiteLLMConfig(
                base_url="http://localhost:4000",
                api_key="sk-litellm",
                model="cognee-llm",
            ),
            embeddings=OllamaEmbeddingConfig(
                base_url="http://localhost:11434",
                model="nomic-embed-text:latest",
                dimensions=768,
            ),
            database=DatabaseConfig(
                db_provider="sqlite",
                graph_provider="kuzu",
                vector_provider="lancedb",
            ),
        )

    @classmethod
    def p2p_shared(cls, litellm_host: str = "localhost", db_host: str = "localhost") -> "CogneeConfig":
        """Config for P2P with shared databases on a LAN node."""
        return cls(
            litellm=LiteLLMConfig(
                base_url=f"http://{litellm_host}:4000",
                api_key="sk-litellm",
                model="cognee-llm",
            ),
            embeddings=OllamaEmbeddingConfig(
                base_url="http://localhost:11434",
                model="nomic-embed-text:latest",
                dimensions=768,
            ),
            database=DatabaseConfig(
                db_provider="postgres",
                db_host=db_host,
                db_port=5432,
                db_username="cognee",
                db_password="cognee",
                db_name="cognee_db",
                graph_provider="neo4j",
                graph_url=f"bolt://{db_host}:7687",
                graph_username="neo4j",
                graph_password=os.environ.get("NEO4J_PASSWORD", "changeme"),
                vector_provider="qdrant",
                vector_url=f"http://{db_host}:6333",
            ),
        )
