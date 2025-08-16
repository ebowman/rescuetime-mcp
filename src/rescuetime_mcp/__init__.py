"""RescueTime MCP Server package."""

__version__ = "0.1.0"
__author__ = "Eric Bowman"
__email__ = "eric@example.com"
__description__ = "FastMCP server for RescueTime API integration"

from .client import RescueTimeClient
from .server import create_server

__all__ = ["RescueTimeClient", "create_server"]
