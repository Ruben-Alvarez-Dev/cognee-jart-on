#!/bin/bash
# COGNEE-jart-on — Setup script
# Run this on the Mac Mini to start all services

set -e

echo "=========================================="
echo "  COGNEE-jart-on — Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Install Docker Desktop first."
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama not found. Install with: brew install ollama"
fi

echo "  Docker: OK"
echo "  Ollama: $(ollama --version 2>/dev/null || echo 'not found')"
echo ""

# Check embedding model
echo "[2/5] Checking Ollama embedding model..."
if ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
    echo "  nomic-embed-text: OK"
else
    echo "  Pulling nomic-embed-text..."
    ollama pull nomic-embed-text:latest
fi
echo ""

# Check .env
echo "[3/5] Checking configuration..."
if [ ! -f .env ]; then
    echo "  Creating .env from template..."
    cp docs/services/env-template.txt .env
    echo "  IMPORTANT: Edit .env and set your LLM API key!"
    echo "  Then run this script again."
    exit 0
fi
echo "  .env: OK"
echo ""

# Start services
echo "[4/5] Starting Docker services..."
docker compose up -d
echo ""

# Wait for services
echo "[5/5] Waiting for services to be ready..."
sleep 5

# Check health
echo ""
echo "Service status:"
echo "  PostgreSQL: $(docker inspect cognee-postgres --format='{{.State.Status}}' 2>/dev/null || echo 'not running')"
echo "  Neo4j:      $(docker inspect cognee-neo4j --format='{{.State.Status}}' 2>/dev/null || echo 'not running')"
echo "  LiteLLM:    $(docker inspect cognee-litellm --format='{{.State.Status}}' 2>/dev/null || echo 'not running')"
echo "  Ollama:     $(curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo 'running' || echo 'not running')"
echo ""

echo "=========================================="
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit .env if you haven't set your API key"
echo "  2. Test: python examples/basic_usage.py"
echo "  3. CLI:  cognee-jart-on init"
echo "=========================================="
