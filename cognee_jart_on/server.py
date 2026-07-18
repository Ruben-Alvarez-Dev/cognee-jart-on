"""
Cognee API server wrapper for COGNEE-jart-on.

Wraps Cognee's built-in FastAPI server with the jart-on configuration.
This is the central API that P2P peers connect to via cognee.serve().

Usage:
    from cognee_jart_on.server import run_server
    run_server(host="0.0.0.0", port=8000)
"""

from __future__ import annotations

import logging
from typing import Optional

from .config import CogneeConfig

logger = logging.getLogger("cognee-jart-on.server")


async def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    config: Optional[CogneeConfig] = None,
) -> None:
    """Start the Cognee API server with jart-on configuration.

    This exposes the full Cognee REST API for P2P peers to connect to
    via cognee.serve(url="http://this-host:port").

    Args:
        host: Bind address. Use "0.0.0.0" for LAN access.
        port: Bind port. Default 8000.
        config: CogneeConfig. If None, builds from environment.
    """
    from .bootstrap import setup_cognee

    await setup_cognee(config)

    import uvicorn

    # Cognee exposes its own FastAPI app
    from cognee.api.client import app

    logger.info("Starting COGNEE-jart-on API server on %s:%d", host, port)
    logger.info("Peers can connect with: cognee.serve(url='http://<this-host>:%d')", port)

    uvicorn_config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    config: Optional[CogneeConfig] = None,
) -> None:
    """Synchronous wrapper to start the server.

    Args:
        host: Bind address. Use "0.0.0.0" for LAN access.
        port: Bind port. Default 8000.
        config: CogneeConfig. If None, builds from environment.
    """
    import asyncio
    asyncio.run(start_server(host, port, config))
