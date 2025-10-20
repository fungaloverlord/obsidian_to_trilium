#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Loading configuration from .env file..."
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
else
    echo "Error: .env file not found at $SCRIPT_DIR/.env"
    echo "Please create a .env file based on .env.example"
    exit 1
fi

# Check required variables
if [ -z "$TRILIUM_TOKEN" ]; then
    echo "Error: TRILIUM_TOKEN not set in .env file"
    exit 1
fi

if [ -z "$SOURCE_DIR" ]; then
    echo "Error: SOURCE_DIR not set in .env file"
    exit 1
fi

# Build command with optional parameters
CMD="$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/md_to_trilium.py"
CMD="$CMD --token $TRILIUM_TOKEN"

if [ -n "$TRILIUM_SERVER" ]; then
    CMD="$CMD --server $TRILIUM_SERVER"
fi

if [ -n "$TRILIUM_PARENT_NOTE" ]; then
    CMD="$CMD --parent $TRILIUM_PARENT_NOTE"
fi

CMD="$CMD $SOURCE_DIR"

# Execute the command
echo "Running: md_to_trilium.py"
echo "Source: $SOURCE_DIR"
echo "Server: ${TRILIUM_SERVER:-http://localhost:8080}"
echo "Parent: ${TRILIUM_PARENT_NOTE:-root}"
echo ""

$CMD