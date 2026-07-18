# COGNEE-jart-on

> Cognee jarta on — P2P integration for Cognee with LiteLLM proxy and local embeddings.

## What is this?

**COGNEE-jart-on** is a [Cognee](https://github.com/topoteretes/cognee) integration that adds:

- **LLM via LiteLLM proxy** — Cognee talks to LiteLLM (OpenAI-compatible), LiteLLM forwards to the real provider
- **Local embeddings via Ollama** — CPU-based, no external API needed
- **P2P shared knowledge base** — Multiple devices on a LAN share the same graph/vector/relational stores
- **MCP server** — Direct integration with Pi Agent and other MCP clients

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Mac Mini (Services)                                    │
│  ├── LiteLLM Proxy (:4000)     → LLM real (API)        │
│  ├── PostgreSQL (:5432)        → relational store       │
│  ├── Neo4j (:7687)             → knowledge graph        │
│  ├── Qdrant (:6333)            → vector store           │
│  └── Ollama (:11434)           → embeddings (CPU)       │
└──────────────────┬──────────────────────────────────────┘
                   │ LAN
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
 iPhone        iPad        Mac Laptop
 Cognee        Cognee      Cognee
 Ollama(emb)   Ollama(emb) Ollama(emb)
 ──read/write──► shared DBs ◄──read/write──
```

## Quick start

### 1. Start services on Mac Mini

```bash
# Set your real LLM API key
export LITELLM_LLM_API_KEY="sk-your-real-key"

# Start all services
docker compose up -d

# Pull embedding model on Ollama (runs natively, not in Docker)
ollama pull nomic-embed-text:latest
```

### 2. Install on each peer device

```bash
pip install cognee-jart-on

# Each peer also needs Ollama for local embeddings
ollama pull nomic-embed-text:latest
```

### 3. Use from Python

```python
from cognee_jart_on import CogneeConfig, setup_cognee

# Local development (all local)
config = CogneeConfig.local_dev()

# P2P with shared DBs (point to Mac Mini IP)
config = CogneeConfig.p2p_shared(
    litellm_host="192.168.1.100",
    db_host="192.168.1.100",
)

await setup_cognee(config)

import cognee

# Store knowledge
await cognee.remember("Important fact about the project.")

# Query knowledge
results = await cognee.recall("What is the important fact?")
```

### 4. CLI

```bash
# Verify configuration
cognee-jart-on init --litellm-host 192.168.1.100 --shared-db --db-host 192.168.1.100

# Start API server (for other peers to connect)
cognee-jart-on serve --host 0.0.0.0 --port 8000

# Check status
cognee-jart-on status --litellm-host 192.168.1.100

# Start MCP server (stdio)
cognee-jart-on mcp --litellm-host 192.168.1.100
```

## Configuration

### LiteLLM proxy (LLM enmascarado)

Cognee never talks directly to OpenAI/Anthropic/etc. It talks to LiteLLM:

```yaml
# docs/services/litellm_config.yaml
model_list:
  - model_name: cognee-llm
    litellm_params:
      model: openai/gpt-4o-mini     # Your real provider
      api_key: os.environ/LITELLM_LLM_API_KEY
```

Change `model` to any provider LiteLLM supports (OpenAI, Anthropic, Bedrock, Ollama, etc.) without touching Cognee config.

### Ollama embeddings (local)

Each peer runs its own Ollama for embeddings (CPU, no API key):

```bash
ollama pull nomic-embed-text:latest
```

### Shared databases (P2P mode)

For P2P with shared knowledge base, the Mac Mini runs:

| Service   | Port | Purpose              |
|-----------|------|----------------------|
| PostgreSQL | 5432 | Relational store     |
| Neo4j     | 7687 | Knowledge graph      |
| Qdrant    | 6333 | Vector store         |
| LiteLLM   | 4000 | LLM proxy            |
| Ollama    | 11434| Embeddings (native)  |

## Project structure

```
cognee-jart-on/
├── cognee_jart_on/
│   ├── __init__.py        # Exports: setup_cognee, CogneeConfig
│   ├── config.py          # Configuration (LiteLLM, Ollama, DBs)
│   ├── bootstrap.py       # Setup Cognee with jart-on config
│   ├── tools.py           # Agent tools (remember, recall, etc.)
│   ├── server.py          # FastAPI server wrapper
│   ├── mcp_server.py      # MCP server for Pi Agent
│   └── cli.py             # CLI commands
├── examples/
├── tests/
├── docs/services/         # LiteLLM config
├── docker-compose.yml     # Mac Mini services
└── pyproject.toml
```

## License

MIT

## Credits

- [Cognee](https://github.com/topoteretes/cognee) — AI Memory Platform
- [LiteLLM](https://github.com/BerriAI/litellm) — LLM proxy gateway
- [Ollama](https://ollama.ai) — Local LLM/embedding runtime
- Nombre inspirado en la jartá andaluza
