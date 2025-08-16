"""FastMCP server for RescueTime API integration.

Copyright (c) 2025 Eric Bowman

This software is licensed under the MIT License.
See LICENSE file in the project root for full license text.
"""

import os
from datetime import datetime
from typing import Any, Optional, Union

import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

from .client import (
    AlertsFeedRequest,
    AnalyticDataRequest,
    DailySummaryRequest,
    HighlightPost,
    OfflineTimePost,
    PerspectiveType,
    RescueTimeClient,
    ResolutionTime,
    RestrictKind,
)

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def create_server() -> FastMCP:
    """Create and configure the FastMCP server."""

    # Get API key from environment
    api_key = os.getenv("RESCUETIME_API_KEY")

    if not api_key:
        raise ValueError("RESCUETIME_API_KEY environment variable is required")

    # Create FastMCP server
    mcp = FastMCP("RescueTime MCP Server")

    # Store client instance
    client_instance: Optional[RescueTimeClient] = None

    async def get_client() -> RescueTimeClient:
        """Get or create RescueTime client instance."""
        nonlocal client_instance
        if client_instance is None:
            client_instance = RescueTimeClient(api_key=api_key)
        return client_instance

    @mcp.tool()
    async def get_analytic_data(
        perspective: str = "rank",
        resolution_time: str = "hour",
        restrict_begin: Optional[str] = None,
        restrict_end: Optional[str] = None,
        restrict_kind: Optional[str] = None,
        restrict_project: Optional[str] = None,
        restrict_thing: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get analytic data from RescueTime API.

        Args:
            perspective: Data perspective - 'rank', 'interval', or 'member'
            resolution_time: Time resolution - 'minute', 'hour', 'day', 'week', or 'month'
            restrict_begin: Start date in YYYY-MM-DD format
            restrict_end: End date in YYYY-MM-DD format
            restrict_kind: Restrict by 'category', 'activity', 'productivity', 'document', or 'overview'
            restrict_project: Filter by specific project name
            restrict_thing: Filter by specific activity or category name

        Returns:
            Dictionary containing analytic data from RescueTime
        """
        try:
            client = await get_client()

            request = AnalyticDataRequest(
                perspective=PerspectiveType(perspective),
                resolution_time=ResolutionTime(resolution_time),
                restrict_begin=restrict_begin,
                restrict_end=restrict_end,
                restrict_kind=RestrictKind(restrict_kind) if restrict_kind else None,
                restrict_project=restrict_project,
                restrict_thing=restrict_thing,
            )

            result = await client.get_analytic_data(request)
            logger.info(
                "Retrieved analytic data",
                perspective=perspective,
                resolution_time=resolution_time,
            )
            return result

        except Exception as e:
            logger.error("Error getting analytic data", error=str(e))
            raise RuntimeError(f"Failed to get analytic data: {str(e)}")

    @mcp.tool()
    async def get_daily_summary_feed(
        restrict_begin: Optional[str] = None,
        restrict_end: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get daily summary feed from RescueTime API.

        Args:
            restrict_begin: Start date in YYYY-MM-DD format
            restrict_end: End date in YYYY-MM-DD format

        Returns:
            Dictionary containing daily summary data
        """
        try:
            client = await get_client()

            request = None
            if restrict_begin or restrict_end:
                request = DailySummaryRequest(
                    restrict_begin=restrict_begin,
                    restrict_end=restrict_end,
                )

            result = await client.get_daily_summary_feed(request)
            logger.info(
                "Retrieved daily summary feed", begin=restrict_begin, end=restrict_end
            )
            
            # Wrap list responses in a dict structure for MCP compatibility
            if isinstance(result, list):
                return {
                    "summaries": result,
                    "count": len(result),
                    "date_range": {
                        "begin": restrict_begin,
                        "end": restrict_end
                    }
                }
            return result

        except Exception as e:
            logger.error("Error getting daily summary feed", error=str(e))
            raise RuntimeError(f"Failed to get daily summary feed: {str(e)}")

    @mcp.tool()
    async def get_alerts_feed(op: str = "list") -> dict[str, Any]:
        """Get alerts feed from RescueTime API.

        Args:
            op: Operation to perform - 'list' to get alerts or 'dismiss' to dismiss alerts

        Returns:
            Dictionary containing alerts data
        """
        try:
            client = await get_client()

            request = AlertsFeedRequest(op=op)
            result = await client.get_alerts_feed(request)
            logger.info("Retrieved alerts feed", operation=op)
            
            # Wrap list responses in a dict structure for MCP compatibility
            if isinstance(result, list):
                return {
                    "alerts": result,
                    "count": len(result),
                    "operation": op
                }
            return result

        except Exception as e:
            logger.error("Error getting alerts feed", error=str(e))
            raise RuntimeError(f"Failed to get alerts feed: {str(e)}")

    @mcp.tool()
    async def dismiss_alert(alert_id: int) -> dict[str, Any]:
        """Dismiss a specific alert in RescueTime.

        Args:
            alert_id: ID of the alert to dismiss

        Returns:
            Dictionary containing dismiss operation result
        """
        try:
            client = await get_client()

            result = await client.dismiss_alert(alert_id)
            logger.info("Dismissed alert", alert_id=alert_id)
            return result

        except Exception as e:
            logger.error("Error dismissing alert", error=str(e), alert_id=alert_id)
            raise RuntimeError(f"Failed to dismiss alert {alert_id}: {str(e)}")

    @mcp.tool()
    async def get_highlights_feed(
        restrict_begin: Optional[str] = None,
        restrict_end: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get highlights feed from RescueTime API.

        Args:
            restrict_begin: Start date in YYYY-MM-DD format
            restrict_end: End date in YYYY-MM-DD format

        Returns:
            Dictionary containing highlights data
        """
        try:
            client = await get_client()

            result = await client.get_highlights_feed(restrict_begin, restrict_end)
            logger.info(
                "Retrieved highlights feed", begin=restrict_begin, end=restrict_end
            )
            
            # Wrap list responses in a dict structure for MCP compatibility
            if isinstance(result, list):
                return {
                    "highlights": result,
                    "count": len(result),
                    "date_range": {
                        "begin": restrict_begin,
                        "end": restrict_end
                    }
                }
            return result

        except Exception as e:
            logger.error("Error getting highlights feed", error=str(e))
            raise RuntimeError(f"Failed to get highlights feed: {str(e)}")

    @mcp.tool()
    async def post_highlight(
        highlight_date: str,
        description: str,
        source: Optional[str] = None,
    ) -> dict[str, Any]:
        """Post a new highlight to RescueTime.

        Args:
            highlight_date: Date for the highlight in YYYY-MM-DD format
            description: Description of the highlight
            source: Optional source information

        Returns:
            Dictionary containing post operation result
        """
        try:
            client = await get_client()

            highlight = HighlightPost(
                highlight_date=highlight_date,
                description=description,
                source=source,
            )

            result = await client.post_highlight(highlight)
            logger.info(
                "Posted highlight", date=highlight_date, description=description
            )
            return result

        except Exception as e:
            logger.error("Error posting highlight", error=str(e))
            raise RuntimeError(f"Failed to post highlight: {str(e)}")

    @mcp.tool()
    async def start_focus_session(duration: Optional[int] = None) -> dict[str, Any]:
        """Start a FocusTime session in RescueTime.

        Args:
            duration: Optional session duration in minutes

        Returns:
            Dictionary containing session start result
        """
        try:
            client = await get_client()

            result = await client.start_focus_session(duration)
            logger.info("Started focus session", duration=duration)
            return result

        except Exception as e:
            logger.error("Error starting focus session", error=str(e))
            raise RuntimeError(f"Failed to start focus session: {str(e)}")

    @mcp.tool()
    async def end_focus_session() -> dict[str, Any]:
        """End the current FocusTime session in RescueTime.

        Returns:
            Dictionary containing session end result
        """
        try:
            client = await get_client()

            result = await client.end_focus_session()
            logger.info("Ended focus session")
            return result

        except Exception as e:
            logger.error("Error ending focus session", error=str(e))
            raise RuntimeError(f"Failed to end focus session: {str(e)}")

    @mcp.tool()
    async def get_focus_session_status() -> dict[str, Any]:
        """Get current FocusTime session status from RescueTime.

        Returns:
            Dictionary containing current focus session status
        """
        try:
            client = await get_client()

            result = await client.get_focus_session_status()
            logger.info("Retrieved focus session status")
            return result

        except Exception as e:
            logger.error("Error getting focus session status", error=str(e))
            raise RuntimeError(f"Failed to get focus session status: {str(e)}")

    @mcp.tool()
    async def post_offline_time(
        offline_date: str,
        offline_hours: float,
        description: str,
    ) -> dict[str, Any]:
        """Post offline time to RescueTime.

        Args:
            offline_date: Date for the offline time in YYYY-MM-DD format
            offline_hours: Number of offline hours (can be decimal)
            description: Description of the offline time

        Returns:
            Dictionary containing post operation result
        """
        try:
            client = await get_client()

            offline_time = OfflineTimePost(
                offline_date=offline_date,
                offline_hours=offline_hours,
                description=description,
            )

            result = await client.post_offline_time(offline_time)
            logger.info("Posted offline time", date=offline_date, hours=offline_hours)
            return result

        except Exception as e:
            logger.error("Error posting offline time", error=str(e))
            raise RuntimeError(f"Failed to post offline time: {str(e)}")

    @mcp.tool()
    async def health_check() -> dict[str, Any]:
        """Check the health of the RescueTime API connection.

        Returns:
            Dictionary containing health check results
        """
        try:
            client = await get_client()

            is_healthy = await client.health_check()
            result = {
                "healthy": is_healthy,
                "timestamp": datetime.now().isoformat(),
                "api_key_valid": is_healthy,
            }

            logger.info("Health check completed", healthy=is_healthy)
            return result

        except Exception as e:
            logger.error("Error during health check", error=str(e))
            return {
                "healthy": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    # Cleanup handler for when server shuts down
    async def cleanup():
        """Clean up resources when server shuts down."""
        nonlocal client_instance
        if client_instance:
            await client_instance.close()
            client_instance = None

    # Store cleanup function for external access
    mcp._cleanup = cleanup

    return mcp


def main():
    """Main entry point for the RescueTime MCP server."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        from . import __version__

        print(f"rescuetime-mcp {__version__}")
        return

    try:
        server = create_server()
        logger.info("Starting RescueTime MCP server")
        server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server error", error=str(e))
        raise


if __name__ == "__main__":
    main()
