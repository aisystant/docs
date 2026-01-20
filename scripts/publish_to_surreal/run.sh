#!/bin/bash
#
# Publish documentation to SurrealDB
#
# Usage:
#   ./run.sh              # Normal publish (update existing data)
#   ./run.sh --clear      # Clear and republish all data
#   ./run.sh --dry-run    # Parse only, don't write to database
#
# Configuration:
#   Create a .env file with your credentials (see .env.example)
#   Or set environment variables directly.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the publisher (.env is loaded by Python)
echo "Running publisher..."
python main.py "$@"
