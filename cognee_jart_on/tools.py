"""
Cognee tools for agent frameworks.

Provides remember/recall/improve/forget as callable tools
compatible with Strands, LangGraph, CrewAI, and other agent frameworks.

Usage:
    from cognee_jart_on.tools import cognee_tools

    # With Strands
    from strands import Agent
    agent = Agent(tools=cognee_tools())

    # Individual tools
    from cognee_jart_on.tools import remember, recall
"""

from __future__ import annotations

import json
from typing import Any, Optional


async def remember(
    data: str,
    dataset_name: str = "main_dataset",
    session_id: Optional[str] = None,
) -> str:
    """Store content in Cognee's permanent knowledge graph or session cache.

    Args:
        data: Text content to store (required).
        dataset_name: Target dataset name. Defaults to "main_dataset".
        session_id: If set, stores in session cache instead of permanent graph.

    Returns:
        JSON string with operation result.
    """
    try:
        import cognee

        result = await cognee.remember(
            data=data,
            dataset_name=dataset_name,
            session_id=session_id,
        )
        return json.dumps({
            "status": str(result.status) if hasattr(result, "status") else "completed",
            "dataset_name": dataset_name,
            "session_id": session_id,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


async def recall(
    query: str,
    datasets: Optional[str] = None,
    session_id: Optional[str] = None,
    top_k: int = 15,
) -> str:
    """Search Cognee's knowledge graph with auto-routing.

    Args:
        query: Natural-language query (required).
        datasets: Comma-separated dataset names to scope search.
        session_id: Session ID for session-aware retrieval.
        top_k: Maximum number of results (1-100). Defaults to 15.

    Returns:
        JSON string with search results.
    """
    try:
        import cognee

        kwargs: dict[str, Any] = {"query_text": query, "top_k": top_k}
        if datasets:
            kwargs["datasets"] = [d.strip() for d in datasets.split(",")]
        if session_id:
            kwargs["session_id"] = session_id

        results = await cognee.recall(**kwargs)

        formatted = []
        for r in results:
            entry = {
                "text": getattr(r, "text", str(r)),
                "source": getattr(r, "source", "unknown"),
            }
            if hasattr(r, "metadata") and r.metadata:
                entry["metadata"] = r.metadata
            formatted.append(entry)

        return json.dumps({"results": formatted, "count": len(formatted)})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


async def improve(
    dataset_name: str = "main_dataset",
    session_ids: Optional[str] = None,
) -> str:
    """Enrich an existing graph and optionally bridge session memory.

    Args:
        dataset_name: Dataset to improve. Defaults to "main_dataset".
        session_ids: Comma-separated session IDs to bridge into permanent graph.

    Returns:
        JSON string with operation result.
    """
    try:
        import cognee

        kwargs: dict[str, Any] = {"dataset": dataset_name}
        if session_ids:
            kwargs["session_ids"] = [s.strip() for s in session_ids.split(",")]

        result = await cognee.improve(**kwargs)
        return json.dumps({
            "status": "completed",
            "dataset_name": dataset_name,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


async def forget(
    dataset_name: Optional[str] = None,
    everything: bool = False,
) -> str:
    """Delete a dataset or wipe all memory.

    Args:
        dataset_name: Dataset name to delete.
        everything: If True, deletes all user-owned memory.

    Returns:
        JSON string with operation result.
    """
    try:
        import cognee

        kwargs: dict[str, Any] = {}
        if dataset_name:
            kwargs["dataset"] = dataset_name
        if everything:
            kwargs["everything"] = True

        result = await cognee.forget(**kwargs)
        return json.dumps({"status": "completed", "result": str(result)})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


async def list_datasets() -> str:
    """List all available datasets.

    Returns:
        JSON string with dataset list.
    """
    try:
        import cognee

        datasets = await cognee.datasets.list_datasets()
        return json.dumps({
            "datasets": [
                {"id": str(d.id), "name": d.name}
                for d in datasets
            ],
            "count": len(datasets),
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def cognee_tools(session_id: Optional[str] = None) -> list:
    """Return Cognee tools as a list for agent frameworks.

    Compatible with Strands, LangGraph, and other frameworks
    that accept tool functions.

    Args:
        session_id: Optional default session ID for session-aware tools.

    Returns:
        List of tool functions.
    """
    tools = [remember, recall, improve, forget, list_datasets]

    if session_id:
        # Only wrap session-aware tools (remember, recall).
        # improve() uses session_ids (plural), forget() and list_datasets()
        # don't accept session_id at all.
        import functools

        def _with_session(func, sid):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if "session_id" not in kwargs:
                    kwargs["session_id"] = sid
                return await func(*args, **kwargs)
            return wrapper

        tools = [
            _with_session(remember, session_id),
            _with_session(recall, session_id),
            improve,
            forget,
            list_datasets,
        ]

    return tools
