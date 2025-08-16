"""RescueTime MCP Server package.

Copyright (c) 2025 Eric Bowman

This software is licensed under the MIT License.
See LICENSE file in the project root for full license text.
"""

__version__ = "0.1.0"
__author__ = "Eric Bowman"
__email__ = "ebowman@boboco.ie"
__description__ = "FastMCP server for RescueTime API integration"

from .client import RescueTimeClient
from .server import create_server

__all__ = ["RescueTimeClient", "create_server"]
