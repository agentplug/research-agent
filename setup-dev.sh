#!/bin/bash

# Development setup script for research-agent
set -e

echo "🚀 Setting up development environment for research-agent..."

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📋 Python version: $python_version"

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to check setup
echo "🧪 Testing pre-commit setup..."
pre-commit run --all-files

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Pre-commit hooks installed:"
echo "   - Code formatting (black, isort)"
echo "   - Linting (flake8, bandit)"
echo "   - Type checking (mypy)"
echo "   - Documentation (pydocstyle)"
echo "   - Security (bandit)"
echo "   - File checks (trailing whitespace, large files, etc.)"
echo ""
echo "🎯 Usage:"
echo "   - Pre-commit will run automatically on git commit"
echo "   - Run manually: pre-commit run --all-files"
echo "   - Skip hooks: git commit --no-verify"
