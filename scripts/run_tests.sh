#!/bin/bash
# Run tests with coverage

set -e  # Exit on error

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run tests with coverage
python -m pytest tests/ --cov=mini_chat --cov-report=term --cov-report=html

# Show coverage report
echo "Coverage report generated in htmlcov/ directory"
