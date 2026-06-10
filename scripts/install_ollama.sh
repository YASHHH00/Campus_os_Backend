#!/bin/bash
set -e

echo "Installing Ollama..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    curl -fsSL https://ollama.com/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install ollama
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Please download the Windows installer from https://ollama.com/download/windows"
    exit 1
else
    echo "Unsupported OS for automatic install. Please install Ollama manually: https://ollama.com"
    exit 1
fi

echo "Starting Ollama service (if not already running)..."
# Just sleep briefly in case it's auto-started by install.sh
sleep 5

echo "Pulling llama3 model..."
ollama pull llama3

echo "Ollama setup complete! Run 'ollama run llama3' to test."
