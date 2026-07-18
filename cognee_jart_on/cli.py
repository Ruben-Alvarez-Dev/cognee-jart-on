"""
CLI for COGNEE-jart-on.

Commands:
- init: Verify configuration and connections
- serve: Start the Cognee API server
- mcp: Start the MCP server
- status: Check service connections
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def cli():
    """COGNEE-jart-on — P2P Cognee integration with LiteLLM proxy."""
    pass


@cli.command()
@click.option("--litellm-host", default="localhost", help="LiteLLM proxy host")
@click.option("--litellm-model", default="cognee-llm", help="Model name on LiteLLM proxy")
@click.option("--ollama-host", default="localhost", help="Ollama host")
@click.option("--ollama-embed-model", default="nomic-embed-text:latest", help="Ollama embedding model")
@click.option("--shared-db", is_flag=True, help="Use shared PostgreSQL/Neo4j/Qdrant instead of local")
@click.option("--db-host", default="localhost", help="Shared database host")
def init(litellm_host, litellm_model, ollama_host, ollama_embed_model, shared_db, db_host):
    """Verify configuration and connections."""
    from .config import CogneeConfig, DatabaseConfig, LiteLLMConfig, OllamaEmbeddingConfig

    config = CogneeConfig(
        litellm=LiteLLMConfig(base_url=f"http://{litellm_host}:4000", model=litellm_model),
        embeddings=OllamaEmbeddingConfig(base_url=f"http://{ollama_host}:11434", model=ollama_embed_model),
        database=DatabaseConfig.p2p_shared(db_host=db_host) if shared_db else DatabaseConfig(),
    )

    console.print("\n[bold]COGNEE-jart-on Configuration[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Service", style="bold")
    table.add_column("Endpoint")
    table.add_column("Details")

    table.add_row("LiteLLM Proxy", config.litellm.base_url, f"model={config.litellm.model}")
    table.add_row("Ollama Embeddings", config.embeddings.base_url, f"model={config.embeddings.model}")
    table.add_row("Database", config.database.db_provider, config.database.db_name)
    table.add_row("Graph DB", config.database.graph_provider, config.database.graph_url or "local")
    table.add_row("Vector DB", config.database.vector_provider, config.database.vector_url or "local")

    console.print(table)

    # Verify connections
    console.print("\n[bold]Verifying connections...[/bold]\n")

    from .bootstrap import verify_connections
    results = asyncio.run(verify_connections(config))

    status_table = Table(show_header=True, header_style="bold")
    status_table.add_column("Service")
    status_table.add_column("Status")

    for service in ["litellm", "ollama", "database", "graph", "vector"]:
        ok = results.get(service, False)
        status = "[green]OK[/green]" if ok else f"[red]FAIL[/red] ({results.get(f'{service}_error', 'unknown')})"
        status_table.add_row(service, status)

    console.print(status_table)

    if all(results.get(s) for s in ["litellm", "ollama", "database", "graph", "vector"]):
        console.print("\n[green bold]All services ready.[/green bold]\n")
    else:
        console.print("\n[red bold]Some services are not reachable. Check the configuration.[/red bold]\n")
        sys.exit(1)


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", help="Bind address")
@click.option("--port", "-p", default=8000, help="Bind port")
@click.option("--litellm-host", default="localhost", help="LiteLLM proxy host")
@click.option("--ollama-host", default="localhost", help="Ollama host")
@click.option("--shared-db", is_flag=True, help="Use shared databases")
@click.option("--db-host", default="localhost", help="Shared database host")
def serve(host, port, litellm_host, ollama_host, shared_db, db_host):
    """Start the Cognee API server for P2P peers."""
    from .config import CogneeConfig, DatabaseConfig, LiteLLMConfig, OllamaEmbeddingConfig

    config = CogneeConfig(
        litellm=LiteLLMConfig(base_url=f"http://{litellm_host}:4000"),
        embeddings=OllamaEmbeddingConfig(base_url=f"http://{ollama_host}:11434"),
        database=(
            DatabaseConfig(
                db_provider="postgres", db_host=db_host,
                graph_provider="neo4j", graph_url=f"bolt://{db_host}:7687",
                graph_username="neo4j", graph_password="cognee-jart-on",
                vector_provider="qdrant", vector_url=f"http://{db_host}:6333",
            )
            if shared_db
            else DatabaseConfig()
        ),
    )

    console.print(f"\n[bold]Starting COGNEE-jart-on server on {host}:{port}[/bold]")
    console.print(f"Peers connect with: [cyan]cognee.serve(url='http://<this-host>:{port}')[/cyan]\n")

    from .server import run_server
    run_server(host=host, port=port, config=config)


@cli.command()
@click.option("--litellm-host", default="localhost", help="LiteLLM proxy host")
@click.option("--ollama-host", default="localhost", help="Ollama host")
def mcp(litellm_host, ollama_host):
    """Start the MCP server (stdio transport)."""
    from .config import CogneeConfig, LiteLLMConfig, OllamaEmbeddingConfig

    config = CogneeConfig(
        litellm=LiteLLMConfig(base_url=f"http://{litellm_host}:4000"),
        embeddings=OllamaEmbeddingConfig(base_url=f"http://{ollama_host}:11434"),
    )

    from .mcp_server import run_mcp_server
    asyncio.run(run_mcp_server(config))


@cli.command()
@click.option("--litellm-host", default="localhost", help="LiteLLM proxy host")
@click.option("--ollama-host", default="localhost", help="Ollama host")
def status(litellm_host, ollama_host):
    """Check service connection status."""
    from .config import CogneeConfig, LiteLLMConfig, OllamaEmbeddingConfig

    config = CogneeConfig(
        litellm=LiteLLMConfig(base_url=f"http://{litellm_host}:4000"),
        embeddings=OllamaEmbeddingConfig(base_url=f"http://{ollama_host}:11434"),
    )

    from .bootstrap import verify_connections
    results = asyncio.run(verify_connections(config))

    table = Table(title="COGNEE-jart-on Status", show_header=True, header_style="bold")
    table.add_column("Service")
    table.add_column("Status")
    table.add_column("Details")

    for service in ["litellm", "ollama", "database", "graph", "vector"]:
        ok = results.get(service, False)
        status_str = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
        detail = results.get(f"{service}_error", "")
        table.add_row(service, status_str, detail)

    console.print(table)


if __name__ == "__main__":
    cli()
