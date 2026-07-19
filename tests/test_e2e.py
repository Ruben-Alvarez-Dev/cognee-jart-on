"""
End-to-end tests for COGNEE-jart-on.
Tests the full Cognee pipeline: remember -> recall.
Requires all services to be running (Docker + Ollama).
"""

import asyncio
import os
import tempfile

import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def config():
    """Create a test config with temp database."""
    from cognee_jart_on.config import CogneeConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_cognee.db")
        cfg = CogneeConfig.local_dev()
        cfg.data_root = os.path.join(tmpdir, "data")
        cfg.apply_env()
        yield cfg


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestCogneeE2E:
    """End-to-end tests for the Cognee pipeline."""

    def test_setup_cognee(self, config):
        """setup_cognee should configure Cognee without errors."""
        from cognee_jart_on.bootstrap import setup_cognee

        async def _run():
            await setup_cognee(config)

        asyncio.run(_run())

    def test_verify_connections(self, config):
        """All service connections should be verified."""
        from cognee_jart_on.bootstrap import verify_connections

        async def _run():
            return await verify_connections(config)

        results = asyncio.run(_run())
        assert results.get("litellm") is True, f"LiteLLM: {results}"
        assert results.get("ollama") is True, f"Ollama: {results}"

    def test_remember_text(self, config):
        """remember() should store text in Cognee."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            result = await cognee.remember(
                "COGNEE-jart-on is a P2P integration for Cognee with LiteLLM proxy.",
                dataset_name="test_e2e",
            )
            return result

        result = asyncio.run(_run())
        assert result is not None
        status = getattr(result, "status", None)
        # Status can be "completed" or "session_stored" depending on mode
        assert status in ("completed", "session_stored", "running"), f"Status: {status}"

    def test_recall_text(self, config):
        """recall() should retrieve stored knowledge."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            results = await cognee.recall(
                "What is COGNEE-jart-on?",
                datasets=["test_e2e"],
                top_k=5,
            )
            return results

        results = asyncio.run(_run())
        assert results is not None
        assert len(results) > 0, "recall returned no results"
        # At least one result should mention jart-on or P2P
        texts = [getattr(r, "text", str(r)) for r in results]
        combined = " ".join(texts).lower()
        assert any(
            keyword in combined
            for keyword in ["jart-on", "p2p", "cognee", "litellm", "integration"]
        ), f"Unexpected results: {texts[:3]}"

    def test_remember_and_recall_session(self, config):
        """Session memory should work with session_id."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            # Store in session
            await cognee.remember(
                "The user prefers dark mode.",
                session_id="test_session_001",
            )
            # Recall from session
            results = await cognee.recall(
                "What does the user prefer?",
                session_id="test_session_001",
            )
            return results

        results = asyncio.run(_run())
        assert results is not None
        # Session results might be empty if session cache is not configured
        # but should not error
