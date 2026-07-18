"""
Basic usage example for COGNEE-jart-on.

Shows how to set up Cognee with LiteLLM proxy + Ollama embeddings,
then use remember/recall to store and query knowledge.
"""

import asyncio

from cognee_jart_on import CogneeConfig, setup_cognee


async def main():
    # 1. Configure (local dev mode)
    config = CogneeConfig.local_dev()
    await setup_cognee(config)

    # 2. Import cognee AFTER setup
    import cognee

    # 3. Store knowledge
    print("Storing knowledge...")
    await cognee.remember("Cognee is an open-source AI memory platform.")
    await cognee.remember("COGNEE-jart-on adds P2P sync with LiteLLM proxy.")
    await cognee.remember("LiteLLM acts as a proxy/mask in front of the real LLM API.")

    # 4. Query knowledge
    print("\nQuerying knowledge...")
    results = await cognee.recall("What is COGNEE-jart-on?")
    for r in results:
        print(f"  - {getattr(r, 'text', r)}")

    # 5. Session memory
    print("\nStoring session memory...")
    await cognee.remember(
        "The user prefers Python over JavaScript.",
        session_id="user_preferences",
    )

    results = await cognee.recall(
        "What does the user prefer?",
        session_id="user_preferences",
    )
    for r in results:
        print(f"  - {getattr(r, 'text', r)}")


if __name__ == "__main__":
    asyncio.run(main())
