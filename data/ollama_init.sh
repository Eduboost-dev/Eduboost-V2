#!/bin/bash
# Qwen model initialization script for Docker
# Runs inside the ollama container to pull models

set -euo pipefail

echo "Waiting for Ollama to be ready..."
sleep 5

# Try to pull Qwen 2.5 Coder 14B
echo "Pulling Qwen 2.5 Coder 14B model..."
ollama pull qwen2.5-coder:14b

if [[ $? -eq 0 ]]; then
  echo "✓ Model pulled successfully"
  
  # List available models
  echo "Available models:"
  ollama list
else
  echo "✗ Model pull failed"
  exit 1
fi
