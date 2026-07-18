"""
MCP server for COGNEE-jart-on.

Exposes Cognee's memory operations as MCP tools for Pi Agent
and other MCP-compatible clients.

Usage:
    from cognee_jart_on.mcp_server import run_mcp_server
    run_mcp_server()
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from .config import CogneeConfig

logger = logging.getLogger("cognee-jart-on.mcp")


def create_mcp_server(config: Optional[CogneeConfig] = None):
    """Create MCP server exposing Cognee tools.

    Args:
        config: CogneeConfig. If None, builds from environment.

    Returns:
        Configured MCP server instance.
    """
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    from .bootstrap import setup_cognee

    server = Server("cognee-jart-on")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="remember",
                description="Store content in Cognee's knowledge graph. Permanent memory by default, session cache with session_id.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Text content to store"},
                        "dataset_name": {"type": "string", "default": "main_dataset", "description": "Target dataset"},
                        "session_id": {"type": "string", "description": "Session ID for session cache mode"},
                    },
                    "required": ["data"],
                },
            ),
            Tool(
                name="recall",
                description="Search Cognee's knowledge graph with auto-routing and session awareness.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural-language query"},
                        "datasets": {"type": "string", "description": "Comma-separated dataset names to scope search"},
                        "session_id": {"type": "string", "description": "Session ID for session-aware retrieval"},
                        "top_k": {"type": "integer", "default": 15, "description": "Max results (1-100)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="improve",
                description="Enrich existing graph and optionally bridge session memory into permanent memory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {"type": "string", "default": "main_dataset", "description": "Dataset to improve"},
                        "session_ids": {"type": "string", "description": "Comma-separated session IDs to bridge"},
                    },
                },
            ),
            Tool(
                name="forget",
                description="Delete a dataset or wipe all memory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {"type": "string", "description": "Dataset name to delete"},
                        "everything": {"type": "boolean", "default": False, "description": "Delete all user-owned memory"},
                    },
                },
            ),
            Tool(
                name="list_datasets",
                description="List all available datasets.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="sync_status",
                description="Check connection status to shared services (LiteLLM, Ollama, databases).",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        import cognee

        try:
            if name == "remember":
                result = await cognee.remember(
                    data=arguments["data"],
                    dataset_name=arguments.get("dataset_name", "main_dataset"),
                    session_id=arguments.get("session_id"),
                )
                output = {
                    "status": str(result.status) if hasattr(result, "status") else "completed",
                    "dataset_name": arguments.get("dataset_name", "main_dataset"),
                }

            elif name == "recall":
                kwargs = {
                    "query_text": arguments["query"],
                    "top_k": arguments.get("top_k", 15),
                }
                if arguments.get("datasets"):
                    # Cognee SDK expects list of strings for datasets
                    kwargs["datasets"] = [d.strip() for d in arguments["datasets"].split(",")]
                if arguments.get("session_id"):
                    kwargs["session_id"] = arguments["session_id"]

                results = await cognee.recall(**kwargs)
                formatted = [
                    {
                        "text": getattr(r, "text", str(r)),
                        "source": getattr(r, "source", "unknown"),
                    }
                    for r in results
                ]
                output = {"results": formatted, "count": len(formatted)}

            elif name == "improve":
                # Cognee SDK expects 'dataset' parameter
                kwargs = {"dataset": arguments.get("dataset_name", "main_dataset")}
                if arguments.get("session_ids"):
                    kwargs["session_ids"] = [s.strip() for s in arguments["session_ids"].split(",")]
                await cognee.improve(**kwargs)
                output = {"status": "completed"}

            elif name == "forget":
                kwargs = {}
                if arguments.get("dataset_name"):
                    kwargs["dataset"] = arguments["dataset_name"]
                if arguments.get("everything"):
                    kwargs["everything"] = True
                result = await cognee.forget(**kwargs)
                output = {"status": "completed", "result": str(result)}

            elif name == "list_datasets":
                datasets = await cognee.datasets.list_datasets()
                output = {
                    "datasets": [{"id": str(d.id), "name": d.name} for d in datasets],
                    "count": len(datasets),
                }

            elif name == "sync_status":
                from .bootstrap import verify_connections
                output = await verify_connections(config)

            else:
                output = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(output, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    return server


async def run_mcp_server(config: Optional[CogneeConfig] = None) -> None:
    """Run the MCP server on stdio transport.

    Args:
        config: CogneeConfig. If None, builds from environment.
    """
    from mcp.server.stdio import stdio_server

    from .bootstrap import setup_cognee

    await setup_cognee(config)
    server = create_mcp_server(config)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
