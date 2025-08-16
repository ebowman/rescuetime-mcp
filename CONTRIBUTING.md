# Contributing to RescueTime MCP Server

Thank you for your interest in contributing to the RescueTime MCP Server! This document outlines the process for contributing to this project.

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A RescueTime account with API access

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/rescuetime-mcp.git
   cd rescuetime-mcp
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

6. Copy the environment template:
   ```bash
   cp .env.example .env
   # Edit .env and add your RescueTime API key
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following our coding standards:
   - Write clean, readable code
   - Add type hints to all functions
   - Follow PEP 8 style guidelines
   - Write comprehensive docstrings

3. Add tests for new functionality:
   - Unit tests in `tests/test_*.py`
   - Integration tests if applicable
   - Ensure all tests pass

4. Run the development checks:
   ```bash
   # Format code
   black src tests
   isort src tests
   
   # Lint code
   ruff check src tests
   
   # Type checking
   mypy src
   
   # Run tests
   pytest
   ```

### Testing

We maintain a comprehensive test suite. Please ensure:

- All tests pass: `pytest`
- Code coverage remains high: `pytest --cov=rescuetime_mcp`
- New features include appropriate tests
- Integration tests pass (requires real API key)

### Submitting Changes

1. Commit your changes with a clear, descriptive message:
   ```bash
   git commit -m "feat: add new feature description"
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - Summary of changes made
   - Test results

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatting)
- Use meaningful variable and function names

### Code Quality Tools

We use these tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast linting
- **mypy**: Static type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for quality checks

### Documentation

- Write clear docstrings for all public functions and classes
- Follow Google-style docstring format
- Update README.md if adding new features
- Include type information in docstrings

### Commit Messages

Follow conventional commit format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions or changes
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or stack traces
- Minimal code example if applicable

### Feature Requests

For new features:

- Describe the use case and problem you're solving
- Explain why this would be valuable to other users
- Consider implementation complexity
- Be open to discussion and feedback

### Documentation Improvements

Documentation contributions are always welcome:

- Fix typos or unclear explanations
- Add examples for complex features
- Improve API documentation
- Update installation or setup instructions

## API Integration Guidelines

When working with RescueTime API integration:

- Follow RescueTime API documentation and rate limits
- Handle errors gracefully with appropriate exceptions
- Use appropriate HTTP status codes
- Maintain backwards compatibility when possible
- Add proper logging for debugging

## Release Process

Releases are managed by maintainers. The process includes:

1. Version bump in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create GitHub release
4. Publish to PyPI

## Getting Help

- Create an issue for bug reports or feature requests
- Use GitHub Discussions for questions
- Check existing issues before creating new ones
- Be patient and respectful when asking for help

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special mentions for major features or fixes

Thank you for contributing to RescueTime MCP Server!