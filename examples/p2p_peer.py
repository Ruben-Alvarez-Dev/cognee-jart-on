"""
P2P peer example for COGNEE-jart-on.

Shows how a peer device connects to shared services
(PostgreSQL + Neo4j + Qdrant on the Mac Mini) and operates
on the shared knowledge base.

Prerequisites:
1. Mac Mini running: docker compose up -d
2. Ollama running on Mac Mini with nomic-embed-text
3. LiteLLM proxy configured with your LLM API key
"""

import asyncio

from cognee_jart_on import CogneeConfig, setup_cognee


async def main():
    # Configure for P2P mode
    # Point to the Mac Mini's IP for shared services
    MAC_MINI_IP = "192.168.1.100"  # Change to your Mac Mini's LAN IP

    config = CogneeConfig.p2p_shared(
        litellm_host=MAC_MINI_IP,  # LiteLLM proxy on Mac Mini
        db_host=MAC_MINI_IP,       # PostgreSQL, Neo4j, Qdrant on Mac Mini
    )

    # Ollama embeddings run locally on each peer (CPU)
    # Each peer has its own Ollama for embeddings
    config.embeddings.base_url = "http://localhost:11434"

    await setup_cognee(config)

    import cognee

    # This peer can now read/write to the shared knowledge base
    print("Connected to shared KB. Storing knowledge...")

    await cognee.remember(
        "This knowledge was added from a P2P peer device.",
        dataset_name="shared_research",
    )

    print("Querying shared knowledge...")
    results = await cognee.recall("What was added from a peer device?")
    for r in results:
        print(f"  - {getattr(r, 'text', r)}")

    print("\nAll peers see the same knowledge base!")


if __name__ == "__main__":
    asyncio.run(main())
