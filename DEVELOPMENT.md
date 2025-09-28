# Development Guide

This guide covers the development setup, coding standards, and workflow for the research-agent project.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/agentplug/research-agent.git
cd research-agent

# Set up development environment
make setup
# or manually:
# pip install -r requirements-dev.txt
# pre-commit install
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Installation

1. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Verify setup:**
   ```bash
   make test
   ```

## Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality and consistency. These hooks run automatically on every commit.

### Installed Hooks

- **Code Formatting:**
  - `black` - Python code formatting
  - `isort` - Import sorting
  - `prettier` - YAML/JSON/Markdown formatting

- **Linting:**
  - `flake8` - Python linting
  - `bandit` - Security linting
  - `mypy` - Type checking
  - `pydocstyle` - Documentation style

- **File Checks:**
  - `trailing-whitespace` - Remove trailing whitespace
  - `end-of-file-fixer` - Ensure files end with newline
  - `check-yaml` - Validate YAML files
  - `check-added-large-files` - Prevent large files
  - `check-merge-conflict` - Detect merge conflicts
  - `debug-statements` - Remove debug statements

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black

# Skip hooks during commit
git commit --no-verify
```

## Development Commands

Use the Makefile for common development tasks:

```bash
make help          # Show all available commands
make setup         # Complete development setup
make test          # Run tests
make lint          # Run all linting checks
make format        # Format code
make check-types   # Run type checking
make clean         # Clean temporary files
make ci            # Run CI pipeline
```

## Code Standards

### Python Code Style

- **Line Length:** 88 characters (Black standard)
- **Import Style:** Google style with isort
- **Docstrings:** Google format
- **Type Hints:** Required for all functions

### Example Code Style

```python
def research_function(
    query: str,
    mode: str = "instant"
) -> Dict[str, Any]:
    """
    Conduct research with specified parameters.

    Args:
        query: The research query to process
        mode: Research mode (instant, quick, standard, deep)

    Returns:
        Dictionary containing research results

    Raises:
        ValueError: If query is empty
    """
    if not query:
        raise ValueError("Query cannot be empty")

    # Implementation here
    return {"success": True, "data": result}
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_phase1.py -v

# Run with coverage
python -m pytest tests/ --cov=research_agent --cov-report=html
```

### Test Structure

```
tests/
├── test_phase1.py          # Phase 1 tests
├── test_research_agent.py  # Research agent tests
├── test_llm_service.py     # LLM service tests
└── conftest.py            # Test configuration
```

## CI/CD Pipeline

The project uses pre-commit hooks for code quality and consistency:

### Local Development

- **Pre-commit hooks**: Run automatically on every commit
- **Code formatting**: Black and isort
- **File validation**: Basic checks for consistency
- **Security scanning**: Can be enabled with bandit

### Local CI Simulation

```bash
# Run full CI pipeline locally
make ci

# Run specific CI steps
make lint
make test
make check-security
```

## Security

### Security Scanning

```bash
# Run security checks
make check-security

# Check for known vulnerabilities
safety check
```

### Security Best Practices

- No hardcoded secrets or API keys
- Use environment variables for configuration
- Regular dependency updates
- Security linting with bandit

## Contributing

### Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make changes and test:**
   ```bash
   make test
   make lint
   ```

3. **Commit with conventional commits:**
   ```bash
   git commit -m "feat: add new research mode"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feat/your-feature
   ```

### Commit Message Format

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

## Troubleshooting

### Common Issues

1. **Pre-commit hooks failing:**
   ```bash
   # Update hooks
   pre-commit autoupdate

   # Run specific hook to see error
   pre-commit run black --verbose
   ```

2. **Import errors:**
   ```bash
   # Install in development mode
   pip install -e .
   ```

3. **Type checking errors:**
   ```bash
   # Check specific file
   mypy research_agent/research_agent/core.py
   ```

### Getting Help

- Check existing issues on GitHub
- Review the CI logs for detailed error messages
- Run `make help` for available commands
