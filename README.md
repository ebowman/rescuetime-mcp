# RescueTime MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A comprehensive FastMCP server for integrating with the RescueTime API, providing tools to access productivity data, manage focus sessions, and interact with all RescueTime features through the Model Context Protocol (MCP).

## Quick Start (macOS)

Follow these steps in order to get RescueTime MCP working with Claude Desktop:

### Step 1: Get Your RescueTime API Key

1. Log in to your RescueTime account
2. Go to https://www.rescuetime.com/anapi/manage
3. Generate or copy your existing API key (you'll need this for Step 3)

### Step 2: Clone and Set Up the Project

```bash
# Clone the repository
git clone https://github.com/ebowman/rescuetime-mcp.git
cd rescuetime-mcp

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

### Step 3: Create Your Configuration File

Create a `.env` file in the project root with your API key:

```bash
echo "RESCUETIME_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual RescueTime API key from Step 1.

### Step 4: Note Your Installation Path

```bash
# Get the full path to your installation (you'll need this for Step 5)
pwd
# This will output something like: /Users/yourname/projects/rescuetime-mcp
```

### Step 5: Configure Claude Desktop

Open your Claude Desktop configuration file:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add this configuration, replacing `/path/from/step4` with your actual path:

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "/path/from/step4/venv/bin/python",
      "args": ["-m", "rescuetime_mcp.server"]
    }
  }
}
```

For example, if your path from Step 4 was `/Users/john/projects/rescuetime-mcp`, your config would look like:

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "/Users/john/projects/rescuetime-mcp/venv/bin/python",
      "args": ["-m", "rescuetime_mcp.server"]
    }
  }
}
```

### Step 6: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

### Step 7: Test It Works

In Claude Desktop, try asking:
- "Check my RescueTime productivity data for today"
- "Start a 25-minute focus session"
- "Show me my daily productivity summary"

If Claude can access your RescueTime data, you're all set!

## Available Commands in Claude

Once configured, you can ask Claude to:

### Core Functions
- **Get productivity data**: "Show me my RescueTime data for the last week"
- **Daily summaries**: "Get my daily productivity summary" (Note: Has ~24 hour delay, returns previous days only)
- **Manage alerts**: "Show me my RescueTime alerts"
- **Create highlights**: "Add a highlight for completing the project presentation"
- **Focus sessions**: "Start a 45-minute focus session" or "End my focus session"
- **Log offline time**: "Log 2 hours of offline coding work"
- **Check status**: "Is my focus session still active?"

### Convenience Functions
- **Today's productivity score**: "What's my productivity score today?" (Real-time data)
- **Top distractions**: "Show me my top distracting activities today"
- **Latest daily summary**: "Get the most recent daily summary" (Usually yesterday's data)

## Features

- **Complete RescueTime API Coverage**: Access all major RescueTime APIs including analytic data, daily summaries, alerts, highlights, focus sessions, and offline time tracking
- **FastMCP Integration**: Built on the FastMCP framework for robust MCP server functionality
- **Async Support**: Full asynchronous support for high-performance operations
- **Type Safety**: Comprehensive type hints and Pydantic models for data validation
- **Error Handling**: Robust error handling with custom exceptions and logging

## Advanced Configuration

### Alternative API Key Methods

While the `.env` file is recommended, you can also:

1. **Set in Claude Desktop config** (if you prefer not to use .env):
```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "rescuetime_mcp.server"],
      "env": {
        "RESCUETIME_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

2. **Use system environment variable**:
```bash
export RESCUETIME_API_KEY="your_api_key_here"
```

### Windows Installation

The steps are similar, but use:
- `python -m venv venv` instead of `python3`
- `venv\Scripts\activate` instead of `source venv/bin/activate`
- Config file location: `%APPDATA%\Claude\claude_desktop_config.json`

## Development

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=rescuetime_mcp --cov-report=html

# Run integration tests (requires real API key)
export RESCUETIME_API_KEY_REAL="your_real_api_key"
pytest tests/test_integration.py -m integration
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
