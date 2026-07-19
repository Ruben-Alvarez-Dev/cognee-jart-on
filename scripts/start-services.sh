#!/bin/bash
# Start COGNEE-jart-on services with secrets from 1Password
set -e

# Read secrets from 1Password (never printed).
export GEMINI_API_KEY="$(op item get 7265iowkcruygfe3u4pohls25m --fields credential --reveal)"
export NEO4J_PASSWORD="$(op item get xiugrzv3mrpyc7fjfnyatwhaym --fields password --reveal)"

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: Could not read Gemini API key from 1Password (item 7265iowkcruygfe3u4pohls25m)"
  exit 1
fi
if [ -z "$NEO4J_PASSWORD" ]; then
  echo "ERROR: Could not read Neo4j password from 1Password (item xiugrzv3mrpyc7fjfnyatwhaym)"
  exit 1
fi

echo "Starting services with secrets from 1Password..."
docker compose up -d "$@"
echo "Services started. LiteLLM proxy at http://localhost:4000"
echo "Note: for P2P clients, export the same NEO4J_PASSWORD so cognee can"
echo "authenticate against Neo4j:  export NEO4J_PASSWORD=\"\$(op item get xiugrzv3mrpyc7fjfnyatwhaym --fields password --reveal)\""
