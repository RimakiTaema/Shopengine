#!/bin/bash
# Launcher script for shop-converter.py
# This script sets the PYTHONPATH and runs the converter

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include the script directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the shop converter
python3 "$SCRIPT_DIR/shop-converter.py" "$@"