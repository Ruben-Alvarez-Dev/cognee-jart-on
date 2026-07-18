"""
Bootstrap module for COGNEE-jart-on.

Sets up Cognee with the correct configuration for P2P operation:
- LLM via LiteLLM proxy (enmascarado)
- Embeddings via Ollama local
- Shared or local database backends

Usage:
    from cognee_jart_on import setup_cognee, CogneeConfig

    # Local development
    config = CogneeConfig.local_dev()
    await setup_cognee(config)

    # P2P with shared DBs
    config = CogneeConfig.p2p_shared(litellm_host="192.168.1.100")
    await setup_cognee(config)
"""

from __future__ import annotations

import logging
from typing import Optional

from .config import CogneeConfig

logger = logging.getLogger("cognee-jart-on")


async def setup_cognee(config: Optional[CogneeConfig] = None) -> None:
    """Initialize Cognee with COGNEE-jart-on configuration.

    Must be called once at application startup, BEFORE any
    cognee.remember() / cognee.recall() calls.

    Args:
        config: Configuration object. If None, builds from environment variables.
    """
    if config is None:
        config = CogneeConfig.from_env()

    # Apply env vars BEFORE importing cognee
    config.apply_env()

    import cognee

    # Reset Cognee config to pick up new env vars
    # (Cognee caches config on first import, so we force a refresh)
    try:
        cognee.config.set_llm_config({
            "llm_provider": "custom",
            "llm_model": f"custom/{config.litellm.model}",
            "llm_endpoint": f"{config.litellm.base_url}/v1",
            "llm_api_key": config.litellm.api_key,
        })
    except Exception as e:
        logger.warning("Could not set LLM config programmatically: %s (using env vars)", e)

    try:
        cognee.config.set_embedding_config({
            "embedding_provider": "ollama",
            "embedding_model": config.embeddings.model,
            "embedding_endpoint": f"{config.embeddings.base_url}/api/embed",
            "embedding_dimensions": config.embeddings.dimensions,
        })
    except Exception as e:
        logger.warning("Could not set embedding config programmatically: %s (using env vars)", e)

    logger.info(
        "COGNEE-jart-on configured: LLM=%s via %s, Embeddings=%s via %s, DB=%s",
        config.litellm.model,
        config.litellm.base_url,
        config.embeddings.model,
        config.embeddings.base_url,
        config.database.db_provider,
    )


async def verify_connections(config: Optional[CogneeConfig] = None) -> dict:
    """Verify all external service connections.

    Returns dict with status of each service:
    - litellm: LLM proxy reachable
    - ollama: Embedding service reachable
    - database: Relational DB reachable
    - graph: Graph DB reachable
    - vector: Vector DB reachable
    """
    import aiohttp

    if config is None:
        config = CogneeConfig.from_env()

    results = {}

    # Check LiteLLM proxy
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.litellm.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                results["litellm"] = resp.status == 200
    except Exception as e:
        results["litellm"] = False
        results["litellm_error"] = str(e)

    # Check Ollama
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.embeddings.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                results["ollama"] = resp.status == 200
    except Exception as e:
        results["ollama"] = False
        results["ollama_error"] = str(e)

    # Check database (PostgreSQL)
    if config.database.db_provider == "postgres":
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host=config.database.db_host,
                port=config.database.db_port,
                user=config.database.db_username,
                password=config.database.db_password,
                database=config.database.db_name,
                timeout=5,
            )
            await conn.close()
            results["database"] = True
        except Exception as e:
            results["database"] = False
            results["database_error"] = str(e)
    else:
        results["database"] = True  # SQLite always available

    # Check Neo4j
    if config.database.graph_provider == "neo4j":
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                config.database.graph_url,
                auth=(config.database.graph_username, config.database.graph_password),
            )
            driver.verify_connectivity()
            driver.close()
            results["graph"] = True
        except Exception as e:
            results["graph"] = False
            results["graph_error"] = str(e)
    else:
        results["graph"] = True  # Kuzu always available

    # Check Qdrant
    if config.database.vector_provider == "qdrant":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config.database.vector_url}/healthz",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    results["vector"] = resp.status == 200
        except Exception as e:
            results["vector"] = False
            results["vector_error"] = str(e)
    else:
        results["vector"] = True  # LanceDB always available

    return results
