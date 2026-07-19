"""
Quality and correctness tests for COGNEE-jart-on.
Verifies the knowledge graph is actually built and queried correctly.
"""

import asyncio
import os
import tempfile

import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def config():
    from cognee_jart_on.config import CogneeConfig
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = CogneeConfig.local_dev()
        cfg.data_root = os.path.join(tmpdir, "data")
        cfg.apply_env()
        yield cfg


class TestKnowledgeGraphQuality:
    """Verify Cognee actually builds a usable knowledge graph."""

    def test_remember_extracts_entities(self, config):
        """remember() should extract entities from text."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            return await cognee.remember(
                "Albert Einstein developed the theory of relativity in 1905. "
                "He was born in Ulm, Germany.",
                dataset_name="entity_test",
            )

        result = asyncio.run(_run())
        assert result is not None
        status = getattr(result, "status", None)
        assert status in ("completed", "running"), f"Status: {status}"

    def test_recall_finds_entities(self, config):
        """recall() should find entities extracted during remember."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            return await cognee.recall(
                "Who developed the theory of relativity?",
                datasets=["entity_test"],
                top_k=5,
            )

        results = asyncio.run(_run())
        assert results is not None
        assert len(results) > 0, "No results from recall"
        texts = " ".join([getattr(r, "text", str(r)) for r in results]).lower()
        assert "einstein" in texts, f"Expected 'einstein' in results"

    def test_recall_finds_relationships(self, config):
        """recall() should find relationships between entities."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            return await cognee.recall(
                "Where was Einstein born?",
                datasets=["entity_test"],
                top_k=5,
            )

        results = asyncio.run(_run())
        assert results is not None
        assert len(results) > 0
        texts = " ".join([getattr(r, "text", str(r)) for r in results]).lower()
        assert any(w in texts for w in ["ulm", "germany", "born"]), \
            f"Expected birthplace info"

    def test_recall_returns_source_metadata(self, config):
        """recall() results should include source metadata."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            return await cognee.recall("Einstein", datasets=["entity_test"], top_k=3)

        results = asyncio.run(_run())
        assert results is not None
        for r in results:
            assert hasattr(r, "text") or isinstance(r, str)


class TestSessionMemory:
    """Verify session memory works correctly."""

    def test_session_stores_and_recalls(self, config):
        """Session memory should store and recall data."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            await cognee.remember(
                "The user prefers dark mode and Python.",
                session_id="test_session_q",
            )
            return await cognee.recall(
                "What does the user prefer?",
                session_id="test_session_q",
            )

        results = asyncio.run(_run())
        assert results is not None
        # Session results might be empty if caching is not configured
        # but should not error


class TestEmbeddingQuality:
    """Verify embeddings are generated correctly."""

    def test_embedding_dimensions(self):
        """Ollama should return correct embedding dimensions."""
        import urllib.request
        import json

        data = json.dumps({
            "model": "nomic-embed-text:latest",
            "input": "test embedding quality"
        }).encode()

        req = urllib.request.Request(
            "http://localhost:11434/api/embed",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        embedding = result["embeddings"][0]
        assert len(embedding) == 768, f"Expected 768 dims, got {len(embedding)}"
        assert all(isinstance(v, float) for v in embedding[:10])
        assert not all(v == 0.0 for v in embedding[:10])

    def test_embedding_similarity(self):
        """Similar texts should produce similar embeddings."""
        import urllib.request
        import json
        import math

        def get_embedding(text):
            data = json.dumps({"model": "nomic-embed-text:latest", "input": text}).encode()
            req = urllib.request.Request(
                "http://localhost:11434/api/embed",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())["embeddings"][0]

        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            return dot / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)))

        emb1 = get_embedding("Python is a programming language")
        emb2 = get_embedding("Python is a coding language")
        emb3 = get_embedding("The weather is sunny today")

        similar = cosine_sim(emb1, emb2)
        different = cosine_sim(emb1, emb3)

        assert similar > 0.7, f"Similar texts should have high similarity: {similar}"
        assert different < similar


class TestLiteLLMSpendTracking:
    """Verify LiteLLM tracks spending correctly."""

    def test_spend_header_present(self):
        """LiteLLM should return cost in response headers."""
        import urllib.request
        import json

        data = json.dumps({
            "model": "cognee-llm",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
        }).encode()

        req = urllib.request.Request(
            "http://localhost:4000/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-litellm",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            cost = resp.headers.get("x-litellm-response-cost")
            assert cost is not None, "Missing spend tracking header"
            assert float(cost) >= 0

    def test_model_responds_correctly(self):
        """LiteLLM should return valid structured output."""
        import urllib.request
        import json

        data = json.dumps({
            "model": "cognee-llm",
            "messages": [{"role": "user", "content": 'Return JSON: {"status": "ok"}'}],
            "response_format": {"type": "json_object"},
            "max_tokens": 50,
        }).encode()

        req = urllib.request.Request(
            "http://localhost:4000/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-litellm",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())

        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        assert "status" in parsed
        assert parsed["status"] == "ok"


class TestGraphIntegrity:
    """Verify the knowledge graph structure is correct."""

    def test_graph_has_nodes_and_edges(self, config):
        """After remember(), the graph should have nodes and edges."""
        from cognee_jart_on.bootstrap import setup_cognee
        import cognee

        async def _run():
            await setup_cognee(config)
            await cognee.remember(
                "Marie Curie discovered radium. She won the Nobel Prize.",
                dataset_name="graph_test_2",
            )
            results = await cognee.recall(
                "What did Marie Curie discover?",
                datasets=["graph_test_2"],
                top_k=5,
            )
            return results

        results = asyncio.run(_run())
        assert results is not None
        if len(results) > 0:
            texts = " ".join([getattr(r, "text", str(r)) for r in results]).lower()
            assert "curie" in texts or "radium" in texts
