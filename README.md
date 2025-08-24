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
- [Contributing](#contributing)
- [License](#license)

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

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# For users - install basic package
pip install -r requirements.txt
```


## Configuration

### Getting Your RescueTime API Key

1. Log in to your RescueTime account
2. Go to https://www.rescuetime.com/anapi/manage
3. Generate or copy your existing API key

### Configuring for Claude Desktop

To use this MCP server with Claude Desktop, you need to add it to your Claude Desktop configuration:

#### 1. Build and Install the Package (Optional)

If you're using a virtual environment (recommended):

```bash
# From the project root directory
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode
pip install -e .
```

This will install the package in editable mode within your virtual environment.

#### 2. Configure Claude Desktop

Add the server to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to the `mcpServers` section:

**Option 1: Using a virtual environment (recommended):**

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "/path/to/rescuetime-mcp/venv/bin/python",
      "args": ["-m", "rescuetime_mcp.server"],
      "env": {
        "RESCUETIME_API_KEY": "your_rescuetime_api_key_here"
      }
    }
  }
}
```

**Option 2: Using the system Python with PYTHONPATH:**

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "python",
      "args": ["-m", "rescuetime_mcp.server"],
      "env": {
        "RESCUETIME_API_KEY": "your_rescuetime_api_key_here",
        "PYTHONPATH": "/path/to/rescuetime-mcp/src"
      }
    }
  }
}
```

#### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the new MCP server.

#### 4. Verify the Connection

In Claude Desktop, you should now be able to use RescueTime tools. Try asking Claude to check your RescueTime productivity data or start a focus session.

### Environment Variables

For development or standalone usage, you can set your RescueTime API key as an environment variable:

```bash
export RESCUETIME_API_KEY="your_rescuetime_api_key_here"
```

Alternatively, create a `.env` file in the project root:

```env
RESCUETIME_API_KEY=your_rescuetime_api_key_here
```

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

- **`get_analytic_data`** - Get detailed productivity analytics with filters
- **`get_daily_summary_feed`** - Access daily productivity summaries  
- **`get_alerts_feed`** - Retrieve productivity alerts
- **`dismiss_alert`** - Dismiss specific alerts
- **`get_highlights_feed`** - View productivity highlights
- **`post_highlight`** - Create new highlights
- **`start_focus_session`** - Start FocusTime sessions
- **`end_focus_session`** - End current focus session
- **`get_focus_session_status`** - Check focus session status
- **`post_offline_time`** - Log offline work time
- **`health_check`** - Verify API connection

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
├── src/rescuetime_mcp/
│   ├── __init__.py          # Package initialization
│   ├── client.py            # RescueTime API client
│   └── server.py            # FastMCP server implementation
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_client.py       # Client tests  
│   ├── test_server.py       # Server tests
│   └── test_integration.py  # Integration tests
└── pyproject.toml           # Project configuration
```


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code standards, and contribution guidelines.

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

- **Documentation**: This README and inline code documentation
- **Bug Reports**: Use [GitHub Issues](https://github.com/ebowman/rescuetime-mcp/issues) 
- **Feature Requests**: Create an issue with detailed use cases
- **Questions**: Use [GitHub Discussions](https://github.com/ebowman/rescuetime-mcp/discussions)
- **Security**: Email ebowman@boboco.ie for security-related issues

### Project Status

This project is actively maintained. We aim to respond to issues and pull requests promptly.

- **Latest Version**: v0.1.0
- **Python Support**: 3.9+
- **Status**: Beta Release

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

---

**Made with ❤️ by [Eric Bowman](https://github.com/ebowman)**

If this project helps you, please consider giving it a ⭐ on GitHub!
