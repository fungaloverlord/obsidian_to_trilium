#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the CSS upload script
echo "Uploading custom CSS to Trilium..."
echo ""

$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/upload_css.py
