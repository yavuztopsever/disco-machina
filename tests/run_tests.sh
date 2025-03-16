#!/bin/bash
# Run all tests for the DiscoMachina project

# Set script to exit on error
set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$ROOT_DIR"

# Display banner
echo "========================================"
echo "Running DiscoMachina Tests"
echo "========================================"

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit -v

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration -v

# Run end-to-end tests
echo "Running end-to-end tests..."
python -m pytest tests/e2e -v

# Calculate test coverage
echo "Calculating test coverage..."
python -m pytest --cov=src tests/

echo "All tests completed!"