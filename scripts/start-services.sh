#!/bin/bash
# Start COGNEE-jart-on services with secrets from 1Password
set -e

# Read Gemini API key from 1Password
export GEMINI_API_KEY="$(op item get 7265iowkcruygfe3u4pohls25m --fields credential --reveal)"

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: Could not read Gemini API key from 1Password"
  echo "Item ID: 7265iowkcruygfe3u4pohls25m"
  exit 1
fi

echo "Starting services with secrets from 1Password..."
docker compose up -d "$@"
echo "Services started. LiteLLM proxy at http://localhost:4000"
