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
            perspective: string - Data perspective. MUST be exactly 'rank' or 'interval'.
                - 'rank': Shows activities ranked by total time spent (most used first)
                - 'interval': Shows activities broken down by time periods
                NOTE: Only these two values are valid. Other values like 'member', 'team', or 'user' are NOT supported.
            resolution_time: string - Time resolution. MUST be one of: 'minute', 'hour', 'day', 'week', or 'month'
            restrict_begin: string (YYYY-MM-DD format, optional) - Start date for filtering data
            restrict_end: string (YYYY-MM-DD format, optional) - End date for filtering data
            restrict_kind: string (optional) - MUST be one of: 'category', 'activity', 'productivity', 'document', or 'overview'
            restrict_project: string (optional) - Filter by specific project name
            restrict_thing: string (optional) - Filter by specific activity or category name

        Returns:
            Dictionary containing analytic data from RescueTime
        """
        try:
            client = await get_client()

            # Validate perspective with helpful error message
            valid_perspectives = ["rank", "interval"]
            if perspective not in valid_perspectives:
                raise ValueError(
                    f"Invalid perspective '{perspective}'. "
                    f"Must be one of: {', '.join(valid_perspectives)}. "
                    f"'rank' shows activities ranked by time spent, "
                    f"'interval' shows activities broken down by time periods."
                )
            
            # Validate resolution_time with helpful error message
            valid_resolutions = ["minute", "hour", "day", "week", "month"]
            if resolution_time not in valid_resolutions:
                raise ValueError(
                    f"Invalid resolution_time '{resolution_time}'. "
                    f"Must be one of: {', '.join(valid_resolutions)}."
                )

            # Validate restrict_kind if provided
            if restrict_kind and restrict_kind not in ["category", "activity", "productivity", "document", "overview"]:
                raise ValueError(
                    f"Invalid restrict_kind '{restrict_kind}'. "
                    f"Must be one of: 'category', 'activity', 'productivity', 'document', or 'overview'."
                )

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

        except ValueError as e:
            # Pass through our custom validation errors as-is
            logger.error("Validation error in get_analytic_data", error=str(e))
            raise RuntimeError(str(e))
        except Exception as e:
            logger.error("Error getting analytic data", error=str(e))
            raise RuntimeError(f"Failed to get analytic data: {str(e)}")

    @mcp.tool()
    async def get_daily_summary_feed(
        restrict_begin: Optional[str] = None,
        restrict_end: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get processed daily summaries (excludes today due to processing delay).

        IMPORTANT: Daily summaries have a ~24 hour processing delay.
        The API returns summaries only for COMPLETED days (processed after midnight).
        Today's data will NOT be included even if you request it.
        
        Args:
            restrict_begin: string (YYYY-MM-DD format, optional) - Start date (won't include today even if specified)
            restrict_end: string (YYYY-MM-DD format, optional) - End date (won't include today even if specified)

        Returns:
            Dictionary containing daily summary data for completed days only.
            The most recent summary will typically be yesterday's data.
            
        Note: For real-time data from today, use get_analytic_data instead.
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
            op: Operation to perform - 'list' to get alerts

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
    async def get_highlights_feed(
        restrict_begin: Optional[str] = None,
        restrict_end: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get highlights feed from RescueTime API.

        Args:
            restrict_begin: string (YYYY-MM-DD format, optional) - Start date for filtering highlights
            restrict_end: string (YYYY-MM-DD format, optional) - End date for filtering highlights

        Returns:
            Dictionary containing highlights data
            
        Note: When fetching without date filters, results may be cached. For immediate
        visibility of newly posted highlights, use date filters (restrict_begin/restrict_end).
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
            highlight_date: string (YYYY-MM-DD format) - Date for the highlight
            description: string - Description of the highlight
            source: string (optional) - Optional source information

        Returns:
            Dictionary containing post operation result
            
        Note: Posted highlights appear immediately when retrieving with date filters,
        but may not appear in unfiltered feed queries due to caching.
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
    async def start_focus_session(duration: Union[int, str, None] = None) -> dict[str, Any]:
        """Start a FocusTime session in RescueTime.

        Args:
            duration: integer (minutes, optional) - Session duration in minutes. Must be multiple of 5, or -1 for end of day. Default: 30

        Returns:
            Dictionary containing session start result
        """
        try:
            client = await get_client()
            
            # Convert duration to int if it's passed as a string
            if duration is not None:
                if isinstance(duration, str):
                    try:
                        duration = int(duration)
                    except ValueError:
                        raise ValueError(f"Duration must be a valid integer, got: {duration}")
                
                # Validate duration constraints
                if duration != -1 and duration % 5 != 0:
                    raise ValueError(f"Duration must be a multiple of 5 minutes or -1 for end of day, got: {duration}")
                
                if duration < -1 or duration == 0:
                    raise ValueError(f"Duration must be positive, -1 for end of day, or not specified for default (30), got: {duration}")

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
            offline_date: string (YYYY-MM-DD format) - Date for the offline time
            offline_hours: float (decimal hours, e.g., 1.5 for 90 minutes) - Number of offline hours
            description: string - Description of the offline time

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

    @mcp.tool()
    async def get_latest_daily_summary() -> dict[str, Any]:
        """Get the most recent processed daily summary (typically yesterday's data).

        IMPORTANT: RescueTime processes daily summaries overnight at 12:01 AM.
        This function returns the most recent AVAILABLE summary, which is typically yesterday's.
        
        For real-time today data, use get_analytic_data or get_productivity_score instead.

        Returns:
            Dictionary containing the most recent daily summary (usually yesterday's)
            
        Note: This is a convenience wrapper that gets yesterday's summary by default.
        For specific dates, use get_daily_summary_feed with date parameters.
        """
        try:
            from datetime import timedelta
            
            # Get yesterday's date (most recent available summary)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            client = await get_client()
            
            # Request yesterday's summary
            request = DailySummaryRequest(
                restrict_begin=yesterday,
                restrict_end=yesterday
            )
            result = await client.get_daily_summary_feed(request)
            
            # Handle both list and dict responses from the client
            summaries = []
            if isinstance(result, list):
                summaries = result
            elif isinstance(result, dict) and "summaries" in result:
                summaries = result["summaries"]
            
            # Get the first summary (should be yesterday's)
            if summaries:
                latest_summary = summaries[0]
                summary_date = latest_summary.get("date", yesterday)
                
                logger.info("Retrieved latest daily summary", date=summary_date, pulse=latest_summary.get("productivity_pulse"))
                return {
                    "date": summary_date,
                    "summary": latest_summary,
                    "formatted_summary": {
                        "productivity_score": latest_summary.get("productivity_pulse", 0),
                        "total_hours": latest_summary.get("total_hours", 0),
                        "productive_time_percent": latest_summary.get("all_productive_percentage", 0),
                        "distracting_time_percent": latest_summary.get("all_distracting_percentage", 0),
                        "neutral_time_percent": latest_summary.get("neutral_percentage", 0)
                    },
                    "note": "This is the most recent processed daily summary (typically yesterday's data)"
                }
            
            # No summaries available at all
            return {
                "date": yesterday,
                "summary": None,
                "message": "No daily summaries available",
                "note": "Daily summaries require at least one complete day of tracking"
            }
                
        except Exception as e:
            logger.error("Error getting today's summary", error=str(e))
            raise RuntimeError(f"Failed to get today's summary: {str(e)}")

    @mcp.tool()
    async def get_top_distractions(limit: int = 10) -> dict[str, Any]:
        """Get today's top distracting activities from RescueTime.

        This convenience function fetches today's analytic data filtered for
        distracting activities and returns the top time-wasters.

        Args:
            limit: integer (default: 10) - Maximum number of distracting activities to return

        Returns:
            Dictionary containing today's top distracting activities with time spent

        Example:
            ```python
            distractions = await get_top_distractions(5)
            for item in distractions['activities']:
                print(f"{item['activity']}: {item['time_spent_minutes']} minutes")
            ```
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Call the client method directly
            client = await get_client()
            request = AnalyticDataRequest(
                perspective=PerspectiveType.RANK,
                resolution_time=ResolutionTime.HOUR,  # Use hour for more granular data
                restrict_begin=today,
                restrict_end=today
                # Don't use restrict_kind - we want all activities to filter by productivity
            )
            result = await client.get_analytic_data(request)
            
            distracting_activities = []
            
            if "rows" in result:
                for row in result["rows"]:
                    # Row format: [Rank, Time Spent (seconds), Number of People, Activity, Category, Productivity]
                    if len(row) >= 6:
                        productivity_level = row[5]  # Productivity score (-2 to 2)
                        if productivity_level < 0:  # Distracting (-2 or -1)
                            time_seconds = row[1]
                            activity = row[3]
                            category = row[4]
                            
                            distracting_activities.append({
                                "rank": row[0],
                                "activity": activity,
                                "category": category,
                                "time_spent_seconds": time_seconds,
                                "time_spent_minutes": round(time_seconds / 60, 1),
                                "productivity_level": productivity_level,
                                "distraction_level": "Very Distracting" if productivity_level == -2 else "Distracting"
                            })
            
            # Sort by time spent (descending) and limit results
            distracting_activities.sort(key=lambda x: x["time_spent_seconds"], reverse=True)
            top_distractions = distracting_activities[:limit]
            
            total_distraction_time = sum(item["time_spent_seconds"] for item in top_distractions)
            
            logger.info("Retrieved top distractions", date=today, count=len(top_distractions))
            
            return {
                "date": today,
                "activities": top_distractions,
                "summary": {
                    "total_activities": len(top_distractions),
                    "total_distraction_time_minutes": round(total_distraction_time / 60, 1),
                    "total_distraction_time_hours": round(total_distraction_time / 3600, 2)
                }
            }
            
        except Exception as e:
            logger.error("Error getting top distractions", error=str(e))
            raise RuntimeError(f"Failed to get top distractions: {str(e)}")

    @mcp.tool()
    async def get_productivity_score() -> dict[str, Any]:
        """Get today's current productivity metrics from real-time activity data.

        This function calculates productivity metrics from today's actual activity data
        using the analytic API (not the delayed daily summary).

        Returns:
            Dictionary containing productivity metrics calculated from today's activities

        Example:
            ```python
            score = await get_productivity_score()
            print(f"Productive Time: {score['productive_time_hours']} hours")
            print(f"Distracting Time: {score['distracting_time_hours']} hours")
            ```
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            client = await get_client()
            
            # Use analytic data API for real-time data
            request = AnalyticDataRequest(
                perspective=PerspectiveType.RANK,
                resolution_time=ResolutionTime.HOUR,
                restrict_begin=today,
                restrict_end=today
            )
            result = await client.get_analytic_data(request)
            
            if result and "rows" in result:
                rows = result["rows"]
                
                # Calculate productivity metrics from activity data
                total_seconds = 0
                productive_seconds = 0  # Productivity levels 1 and 2
                distracting_seconds = 0  # Productivity levels -1 and -2
                neutral_seconds = 0  # Productivity level 0
                very_productive_seconds = 0  # Level 2
                very_distracting_seconds = 0  # Level -2
                
                for row in rows:
                    seconds = row[1]
                    productivity_level = row[5]
                    
                    total_seconds += seconds
                    
                    if productivity_level == 2:
                        very_productive_seconds += seconds
                        productive_seconds += seconds
                    elif productivity_level == 1:
                        productive_seconds += seconds
                    elif productivity_level == 0:
                        neutral_seconds += seconds
                    elif productivity_level == -1:
                        distracting_seconds += seconds
                    elif productivity_level == -2:
                        very_distracting_seconds += seconds
                        distracting_seconds += seconds
                
                total_hours = total_seconds / 3600
                productive_hours = productive_seconds / 3600
                distracting_hours = distracting_seconds / 3600
                neutral_hours = neutral_seconds / 3600
                
                # Calculate percentages
                productive_percent = (productive_seconds / total_seconds * 100) if total_seconds > 0 else 0
                distracting_percent = (distracting_seconds / total_seconds * 100) if total_seconds > 0 else 0
                neutral_percent = (neutral_seconds / total_seconds * 100) if total_seconds > 0 else 0
                
                # Calculate productivity pulse (weighted score)
                # This is an approximation of RescueTime's formula
                if total_seconds > 0:
                    productivity_pulse = int(
                        ((very_productive_seconds * 1.0 + 
                          (productive_seconds - very_productive_seconds) * 0.75 + 
                          neutral_seconds * 0.5 + 
                          (distracting_seconds - very_distracting_seconds) * 0.25 + 
                          very_distracting_seconds * 0.0) / total_seconds) * 100
                    )
                else:
                    productivity_pulse = 0
                
                # Determine productivity level description
                if productivity_pulse >= 75:
                    level_description = "Excellent"
                elif productivity_pulse >= 60:
                    level_description = "Good"
                elif productivity_pulse >= 40:
                    level_description = "Fair"
                else:
                    level_description = "Needs Improvement"
                
                logger.info("Calculated productivity score from analytic data", date=today, score=productivity_pulse)
                
                return {
                    "date": today,
                    "productivity_pulse": productivity_pulse,
                    "level_description": level_description,
                    "time_breakdown": {
                        "total_hours": round(total_hours, 2),
                        "productive_hours": round(productive_hours, 2),
                        "distracting_hours": round(distracting_hours, 2),
                        "neutral_hours": round(neutral_hours, 2)
                    },
                    "percentages": {
                        "productive": round(productive_percent, 1),
                        "distracting": round(distracting_percent, 1),
                        "neutral": round(neutral_percent, 1)
                    },
                    "detailed_breakdown": {
                        "very_productive_hours": round(very_productive_seconds / 3600, 2),
                        "very_distracting_hours": round(very_distracting_seconds / 3600, 2)
                    },
                    "note": "Calculated from real-time activity data"
                }
            else:
                return {
                    "date": today,
                    "productivity_pulse": 0,
                    "level_description": "No Data",
                    "message": "No productivity data available for today yet"
                }
                
        except Exception as e:
            logger.error("Error getting productivity score", error=str(e))
            raise RuntimeError(f"Failed to get productivity score: {str(e)}")

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
