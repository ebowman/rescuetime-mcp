# RescueTime MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A comprehensive FastMCP server for integrating with the RescueTime API, providing tools to access productivity data, manage focus sessions, and interact with all RescueTime features through the Model Context Protocol (MCP).

## Table of Contents

- [Features](#features)
- [Supported RescueTime APIs](#supported-rescuetime-apis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available MCP Tools](#available-mcp-tools)
- [Development](#development)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **Complete RescueTime API Coverage**: Access all major RescueTime APIs including analytic data, daily summaries, alerts, highlights, focus sessions, and offline time tracking
- **FastMCP Integration**: Built on the FastMCP framework for robust MCP server functionality
- **Async Support**: Full asynchronous support for high-performance operations
- **Type Safety**: Comprehensive type hints and Pydantic models for data validation
- **Error Handling**: Robust error handling with custom exceptions and logging
- **Comprehensive Testing**: Full test suite including unit tests, integration tests, and performance tests

## Supported RescueTime APIs

### 1. Analytic Data API
- Get detailed productivity analytics with customizable time ranges and filters
- Support for different perspectives (rank, interval, member) and resolutions

### 2. Daily Summary Feed API
- Access daily productivity summaries and pulse scores
- Filter by date ranges

### 3. Alerts Feed API
- Retrieve and manage productivity alerts
- Dismiss unwanted alerts

### 4. Highlights Feed/POST API
- View existing highlights
- Create new productivity highlights

### 5. FocusTime APIs
- Start and end focus sessions
- Monitor current focus session status
- Set custom focus duration

### 6. Offline Time POST API
- Log offline work time
- Add descriptions for offline activities

## Installation

### Prerequisites
- Python 3.9 or higher
- RescueTime account with API access
- RescueTime API key

### Install from Source
```bash
# Clone the repository
git clone https://github.com/ebowman/rescuetime-mcp.git
cd rescuetime-mcp

# Install in development mode
pip install -e ".[dev]"
```


## Configuration

### Environment Variables

Set your RescueTime API key as an environment variable:

```bash
export RESCUETIME_API_KEY="your_rescuetime_api_key_here"
```

Alternatively, create a `.env` file in the project root:

```env
RESCUETIME_API_KEY=your_rescuetime_api_key_here
```

### Getting Your API Key

1. Log in to your RescueTime account
2. Go to https://www.rescuetime.com/anapi/manage
3. Generate or copy your existing API key

## Usage

### Running the MCP Server

```bash
# Run directly
rescuetime-mcp

# Or using Python module
python -m rescuetime_mcp.server

# Check version
rescuetime-mcp --version
```

### Available MCP Tools

The server provides the following tools that can be called through MCP:

#### 1. `get_analytic_data`
Get detailed analytics data from RescueTime.

**Parameters:**
- `perspective` (str): Data perspective - 'rank', 'interval', or 'member' (default: 'rank')
- `resolution_time` (str): Time resolution - 'minute', 'hour', 'day', 'week', or 'month' (default: 'hour')
- `restrict_begin` (str, optional): Start date in YYYY-MM-DD format
- `restrict_end` (str, optional): End date in YYYY-MM-DD format
- `restrict_kind` (str, optional): Filter by 'category', 'activity', 'productivity', 'document', or 'overview'
- `restrict_project` (str, optional): Filter by specific project name
- `restrict_thing` (str, optional): Filter by specific activity or category name

#### 2. `get_daily_summary_feed`
Get daily productivity summaries.

**Parameters:**
- `restrict_begin` (str, optional): Start date in YYYY-MM-DD format
- `restrict_end` (str, optional): End date in YYYY-MM-DD format

#### 3. `get_alerts_feed`
Get productivity alerts from RescueTime.

**Parameters:**
- `op` (str): Operation - 'list' to get alerts (default: 'list')

#### 4. `dismiss_alert`
Dismiss a specific alert.

**Parameters:**
- `alert_id` (int): ID of the alert to dismiss

#### 5. `get_highlights_feed`
Get productivity highlights.

**Parameters:**
- `restrict_begin` (str, optional): Start date in YYYY-MM-DD format
- `restrict_end` (str, optional): End date in YYYY-MM-DD format

#### 6. `post_highlight`
Create a new productivity highlight.

**Parameters:**
- `highlight_date` (str): Date for the highlight in YYYY-MM-DD format
- `description` (str): Description of the highlight
- `source` (str, optional): Source information

#### 7. `start_focus_session`
Start a FocusTime session.

**Parameters:**
- `duration` (int, optional): Session duration in minutes

#### 8. `end_focus_session`
End the current FocusTime session.

**Parameters:** None

#### 9. `get_focus_session_status`
Get current FocusTime session status.

**Parameters:** None

#### 10. `post_offline_time`
Log offline time to RescueTime.

**Parameters:**
- `offline_date` (str): Date in YYYY-MM-DD format
- `offline_hours` (float): Number of offline hours (can be decimal)
- `description` (str): Description of the offline time

#### 11. `health_check`
Check the health of the RescueTime API connection.

**Parameters:** None

**Returns:** Health status including API key validity

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ebowman/rescuetime-mcp.git
cd rescuetime-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rescuetime_mcp --cov-report=html

# Run only unit tests
pytest tests/test_client.py tests/test_server.py

# Run integration tests (requires real API key)
export RESCUETIME_API_KEY_REAL="your_real_api_key"
pytest tests/test_integration.py -m integration

# Run performance tests
pytest tests/test_integration.py -m slow
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Project Structure

```
rescuetime-mcp/
├── src/
│   └── rescuetime_mcp/
│       ├── __init__.py          # Package initialization
│       ├── client.py            # RescueTime API client
│       └── server.py            # FastMCP server implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_client.py          # Client tests
│   ├── test_server.py          # Server tests
│   └── test_integration.py     # Integration and performance tests
├── pyproject.toml              # Project configuration
├── requirements.txt            # Production dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## API Reference

### RescueTime API Endpoints

The server integrates with these RescueTime API endpoints:

- **Analytic Data**: `https://www.rescuetime.com/anapi/data`
- **Daily Summary**: `https://www.rescuetime.com/anapi/daily_summary_feed`
- **Alerts Feed**: `https://www.rescuetime.com/anapi/alerts_feed`
- **Highlights Feed**: `https://www.rescuetime.com/anapi/highlights_feed`
- **Highlights Post**: `https://www.rescuetime.com/anapi/highlights_post`
- **FocusTime Start**: `https://www.rescuetime.com/anapi/start_focustime`
- **FocusTime End**: `https://www.rescuetime.com/anapi/end_focustime`
- **FocusTime Status**: `https://www.rescuetime.com/anapi/focustime_status`
- **Offline Time**: `https://www.rescuetime.com/anapi/offline_time_post`

### Error Handling

The client includes comprehensive error handling:

- `RescueTimeAPIError`: Custom exception for API-specific errors
- HTTP status code preservation
- Request timeout handling
- Network error management
- Structured logging for debugging

### Data Models

All API interactions use Pydantic models for validation:

- `AnalyticDataRequest`: Parameters for analytic data queries
- `DailySummaryRequest`: Parameters for daily summary queries
- `AlertsFeedRequest`: Parameters for alerts operations
- `HighlightPost`: Model for creating highlights
- `OfflineTimePost`: Model for logging offline time
- `FocusSessionRequest`: Parameters for focus sessions

## Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) for detailed information about:

- Setting up the development environment
- Code style and quality standards
- Testing requirements
- Pull request process

### Quick Start for Contributors

1. Fork the repository on GitHub
2. Clone your fork and set up the development environment
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes following our coding standards
5. Add tests for new functionality
6. Run the full test suite and quality checks
7. Commit with conventional commit messages
8. Push to your fork and create a Pull Request

### Code Quality

This project maintains high code quality standards:

- **Type Safety**: Full mypy coverage
- **Formatting**: Black and isort
- **Linting**: Ruff for fast, comprehensive linting
- **Testing**: Comprehensive test suite with pytest
- **Pre-commit**: Automated quality checks

### Reporting Issues

- **Bugs**: Use our [bug tracking system](BUGS.md) and GitHub Issues
- **Feature Requests**: Create a GitHub Issue with detailed use cases
- **Security Issues**: Email ebowman@boboco.ie directly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2025 Eric Bowman

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Uses [RescueTime API](https://www.rescuetime.com/anapi/setup/documentation)
- Powered by [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- HTTP client powered by [httpx](https://www.python-httpx.org/)

Special thanks to the FastMCP community and RescueTime for providing robust APIs.

## Support

### Getting Help

- **📖 Documentation**: This README and inline code documentation
- **🐛 Bug Reports**: Use [GitHub Issues](https://github.com/ebowman/rescuetime-mcp/issues) for bug reports
- **💡 Feature Requests**: Create an issue with detailed use cases
- **❓ Questions**: Use [GitHub Discussions](https://github.com/ebowman/rescuetime-mcp/discussions) for community support
- **🔒 Security**: Email ebowman@boboco.ie for security-related issues

### Project Status

This project is actively maintained. We aim to respond to issues and pull requests promptly.

- **Latest Version**: v0.1.0
- **Python Support**: 3.9+
- **Status**: Production Ready ✅

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

---

**Made with ❤️ by [Eric Bowman](https://github.com/ebowman)**

If this project helps you, please consider giving it a ⭐ on GitHub!