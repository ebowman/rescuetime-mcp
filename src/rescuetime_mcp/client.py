"""RescueTime API client implementation.

Copyright (c) 2025 Eric Bowman

This software is licensed under the MIT License.
See LICENSE file in the project root for full license text.
"""

from datetime import date
from enum import Enum
from typing import Any, Optional, Union

import httpx
import structlog
from pydantic import BaseModel, field_validator

logger = structlog.get_logger(__name__)


class PerspectiveType(str, Enum):
    """RescueTime perspective types."""

    RANK = "rank"
    INTERVAL = "interval"


class ResolutionTime(str, Enum):
    """RescueTime resolution time values."""

    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class RestrictKind(str, Enum):
    """RescueTime restrict kind values."""

    CATEGORY = "category"
    ACTIVITY = "activity"
    PRODUCTIVITY = "productivity"
    DOCUMENT = "document"
    OVERVIEW = "overview"


class ProductivityLevel(int, Enum):
    """RescueTime productivity levels."""

    VERY_DISTRACTING = -2
    DISTRACTING = -1
    NEUTRAL = 0
    PRODUCTIVE = 1
    VERY_PRODUCTIVE = 2


class AnalyticDataRequest(BaseModel):
    """Request model for analytic data API."""

    perspective: PerspectiveType = PerspectiveType.RANK
    resolution_time: ResolutionTime = ResolutionTime.HOUR
    restrict_begin: Optional[Union[str, date]] = None
    restrict_end: Optional[Union[str, date]] = None
    restrict_kind: Optional[RestrictKind] = None
    restrict_project: Optional[str] = None
    restrict_thing: Optional[str] = None

    @field_validator("restrict_begin", "restrict_end", mode="before")
    @classmethod
    def validate_dates(cls, v):
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        return v


class DailySummaryRequest(BaseModel):
    """Request model for daily summary feed API."""

    restrict_begin: Optional[Union[str, date]] = None
    restrict_end: Optional[Union[str, date]] = None

    @field_validator("restrict_begin", "restrict_end", mode="before")
    @classmethod
    def validate_dates(cls, v):
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        return v


class AlertsFeedRequest(BaseModel):
    """Request model for alerts feed API."""

    op: str = "list"  # list or dismiss


class HighlightPost(BaseModel):
    """Model for posting highlights."""

    highlight_date: Union[str, date]
    description: str
    source: Optional[str] = None

    @field_validator("highlight_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        return v


class OfflineTimePost(BaseModel):
    """Model for posting offline time."""

    offline_date: Union[str, date]
    offline_hours: Union[int, float]
    description: str

    @field_validator("offline_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        return v


class FocusSessionRequest(BaseModel):
    """Model for focus session requests."""

    duration: Optional[int] = None  # in minutes, for starting sessions


class RescueTimeAPIError(Exception):
    """Custom exception for RescueTime API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RescueTimeClient:
    """Async client for RescueTime API."""

    BASE_URL = "https://www.rescuetime.com/anapi"

    def __init__(self, api_key: str, timeout: int = 30):
        """Initialize the RescueTime client.

        Args:
            api_key: RescueTime API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "User-Agent": "rescuetime-mcp/0.1.0",
                "Accept": "application/json",
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the RescueTime API.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Request body data

        Returns:
            Response data as dictionary

        Raises:
            RescueTimeAPIError: If the API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        params["key"] = self.api_key
        params["format"] = "json"

        logger.debug(
            "Making RescueTime API request", url=url, method=method, params=params
        )

        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            elif method == "POST":
                if data:
                    # For POST requests, add data to params for form encoding
                    params.update(data)
                response = await self.client.post(url, data=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Handle different response formats
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                return response.json()
            else:
                # Some endpoints return plain text or other formats
                return {"response": response.text, "content_type": content_type}

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} error: {e.response.text}"
            logger.error(
                "RescueTime API error",
                error=error_msg,
                status_code=e.response.status_code,
            )
            raise RescueTimeAPIError(
                error_msg, e.response.status_code, {"response": e.response.text}
            )
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error("RescueTime request error", error=error_msg)
            raise RescueTimeAPIError(error_msg)

    async def get_analytic_data(self, request: AnalyticDataRequest) -> dict[str, Any]:
        """Get analytic data from RescueTime.

        Args:
            request: Analytic data request parameters

        Returns:
            Analytic data response
        """
        params = request.model_dump(exclude_none=True, mode="json")
        logger.debug("Analytic data request params", params=params)
        return await self._make_request("data", params=params)

    async def get_daily_summary_feed(
        self, request: Optional[DailySummaryRequest] = None
    ) -> dict[str, Any]:
        """Get daily summary feed from RescueTime.

        Args:
            request: Optional request parameters

        Returns:
            Daily summary feed response
        """
        params = request.model_dump(exclude_none=True) if request else {}
        return await self._make_request("daily_summary_feed", params=params)

    async def get_alerts_feed(
        self, request: Optional[AlertsFeedRequest] = None
    ) -> dict[str, Any]:
        """Get alerts feed from RescueTime.

        Args:
            request: Optional request parameters

        Returns:
            Alerts feed response
        """
        params = request.model_dump(exclude_none=True) if request else {"op": "list"}
        
        # Handle dismiss operations via POST
        if params.get("op") == "dismiss":
            result = await self._make_request("alerts_feed", method="POST", data=params)
            # Handle cases where API returns no structured content for dismiss
            if isinstance(result, dict) and "response" in result:
                return {
                    "status": "dismissed",
                    "operation": "dismiss",
                    "message": result["response"]
                }
            return result if result else {
                "status": "dismissed",
                "operation": "dismiss", 
                "message": "Alert dismissed successfully"
            }
        else:
            return await self._make_request("alerts_feed", params=params)

    async def dismiss_alert(self, alert_id: int) -> dict[str, Any]:
        """Dismiss a specific alert.

        Note: Alert dismissal is not supported by the RescueTime API as of 2025.
        This endpoint is included for completeness but will return an error
        indicating the limitation.

        Args:
            alert_id: ID of the alert to dismiss

        Returns:
            Response indicating API limitation
        """
        # RescueTime API doesn't support alert dismissal operations
        # Return a clear message indicating this limitation
        return {
            "status": "unsupported",
            "alert_id": alert_id,
            "error": "Alert dismissal is not supported by the RescueTime API",
            "message": "The RescueTime API only supports reading alerts, not dismissing them. Please use the RescueTime web interface to dismiss alerts.",
            "api_limitation": True
        }

    async def get_highlights_feed(
        self,
        restrict_begin: Optional[Union[str, date]] = None,
        restrict_end: Optional[Union[str, date]] = None,
    ) -> dict[str, Any]:
        """Get highlights feed from RescueTime.

        Args:
            restrict_begin: Start date filter
            restrict_end: End date filter

        Returns:
            Highlights feed response
        """
        params = {}
        if restrict_begin:
            if isinstance(restrict_begin, date):
                restrict_begin = restrict_begin.strftime("%Y-%m-%d")
            params["restrict_begin"] = restrict_begin
        if restrict_end:
            if isinstance(restrict_end, date):
                restrict_end = restrict_end.strftime("%Y-%m-%d")
            params["restrict_end"] = restrict_end

        return await self._make_request("highlights_feed", params=params)

    async def post_highlight(self, highlight: HighlightPost) -> dict[str, Any]:
        """Post a new highlight to RescueTime.

        Args:
            highlight: Highlight data to post

        Returns:
            Response from post operation
        """
        data = highlight.model_dump(exclude_none=True)
        return await self._make_request("highlights_post", method="POST", data=data)

    async def start_focus_session(
        self, duration: Optional[int] = None
    ) -> dict[str, Any]:
        """Start a FocusTime session.

        Args:
            duration: Session duration in minutes (must be multiple of 5, or -1 for end of day). Default: 30

        Returns:
            Response from start operation
        """
        if duration is None:
            duration = 30  # Default 30 minutes
        data = {"duration": duration}
        result = await self._make_request("start_focustime", method="POST", data=data)
        
        # Handle non-JSON responses  
        if isinstance(result, dict) and "response" in result:
            return {
                "status": "started",
                "duration": duration,
                "message": result["response"]
            }
        return result if result else {
            "status": "started",
            "duration": duration,
            "message": "Focus session started successfully"
        }

    async def end_focus_session(self) -> dict[str, Any]:
        """End the current FocusTime session.

        Returns:
            Response from end operation
        """
        return await self._make_request("end_focustime", method="POST")

    async def get_focus_session_status(self) -> dict[str, Any]:
        """Get current FocusTime session status.

        Returns:
            Current focus session status
        """
        try:
            result = await self._make_request("focustime_started_feed")
            # The API returns a list of recent focus session events
            if isinstance(result, list) and result:
                # Get the most recent session
                latest_session = result[0] if result else None
                return {
                    "active": True,
                    "latest_session": latest_session,
                    "total_sessions": len(result)
                }
            else:
                return {
                    "active": False,
                    "latest_session": None,
                    "total_sessions": 0
                }
        except RescueTimeAPIError as e:
            if e.status_code == 404:
                return {
                    "active": False,
                    "latest_session": None,
                    "message": "No focus session data available"
                }
            raise

    async def post_offline_time(self, offline_time: OfflineTimePost) -> dict[str, Any]:
        """Post offline time to RescueTime.

        Args:
            offline_time: Offline time data to post

        Returns:
            Response from post operation
        """
        data = offline_time.model_dump(exclude_none=True)
        return await self._make_request("offline_time_post", method="POST", data=data)

    async def health_check(self) -> bool:
        """Check if the API key is valid and the service is accessible.

        Returns:
            True if the health check passes, False otherwise
        """
        try:
            # Try a simple API call to validate the key
            await self.get_daily_summary_feed()
            return True
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False
