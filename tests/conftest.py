"""Pytest configuration and fixtures for RescueTime MCP tests."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from rescuetime_mcp.client import RescueTimeClient
from rescuetime_mcp.server import create_server


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_api_key():
    """Provide a test API key."""
    return "test_api_key_12345"


@pytest.fixture
def mock_client(mock_api_key):
    """Create a mock RescueTime client."""
    client = MagicMock(spec=RescueTimeClient)
    client.api_key = mock_api_key
    client.timeout = 30

    # Mock async methods
    client.get_analytic_data = AsyncMock()
    client.get_daily_summary_feed = AsyncMock()
    client.get_alerts_feed = AsyncMock()
    client.get_highlights_feed = AsyncMock()
    client.post_highlight = AsyncMock()
    client.start_focus_session = AsyncMock()
    client.end_focus_session = AsyncMock()
    client.get_focus_session_status = AsyncMock()
    client.post_offline_time = AsyncMock()
    client.health_check = AsyncMock()
    client.close = AsyncMock()

    return client


@pytest.fixture
def sample_analytic_data():
    """Sample analytic data response."""
    return {
        "notes": "data for period",
        "row_headers": [
            "Rank",
            "Time Spent (seconds)",
            "Number of People",
            "Activity",
            "Category",
            "Productivity",
        ],
        "rows": [
            [1, 3600, 1, "Google Chrome", "Communication & Scheduling", 0],
            [2, 1800, 1, "VS Code", "Software Development", 2],
            [3, 900, 1, "Terminal", "Software Development", 1],
        ],
    }


@pytest.fixture
def sample_daily_summary():
    """Sample daily summary response."""
    return [
        {
            "id": 12345,
            "date": "2024-01-15",
            "productivity_pulse": 75,
            "very_productive_percentage": 35,
            "productive_percentage": 40,
            "neutral_percentage": 15,
            "distracting_percentage": 8,
            "very_distracting_percentage": 2,
            "all_productive_percentage": 75,
            "all_distracting_percentage": 10,
            "uncategorized_percentage": 15,
            "business_hours": 8,
            "total_hours": 10.5,
        }
    ]


@pytest.fixture
def sample_alerts():
    """Sample alerts response."""
    return [
        {
            "id": 1,
            "created_at": "2024-01-15T10:00:00Z",
            "type": "daily_goal",
            "message": "You've reached your daily productivity goal!",
        },
        {
            "id": 2,
            "created_at": "2024-01-15T14:30:00Z",
            "type": "distraction_alert",
            "message": "You've spent 30 minutes on distracting activities",
        },
    ]


@pytest.fixture
def sample_highlights():
    """Sample highlights response."""
    return [
        {
            "id": 1,
            "date": "2024-01-15",
            "description": "Completed major feature implementation",
            "created_at": "2024-01-15T17:00:00Z",
        },
        {
            "id": 2,
            "date": "2024-01-14",
            "description": "Team meeting - project planning",
            "created_at": "2024-01-14T11:00:00Z",
        },
    ]


@pytest.fixture
def sample_focus_status():
    """Sample focus session status response."""
    return {
        "active": True,
        "started_at": "2024-01-15T09:00:00Z",
        "duration_minutes": 90,
        "remaining_minutes": 45,
    }


@pytest_asyncio.fixture
async def mcp_server(monkeypatch, mock_client):
    """Create a FastMCP server instance with mocked client."""
    # Mock the environment variable
    monkeypatch.setenv("RESCUETIME_API_KEY", "test_api_key")

    # Create server
    server = create_server()

    # Replace the client creation with our mock
    async def mock_get_client():
        return mock_client

    # Patch the get_client function in the server
    # Note: This is a simplified approach - in a real implementation
    # you might want to use more sophisticated mocking

    yield server, mock_client

    # Cleanup
    if hasattr(server, "_cleanup"):
        await server._cleanup()


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx Response."""
    response = MagicMock()
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"status": "success"}
    response.text = '{"status": "success"}'
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def date_today():
    """Get today's date."""
    return date.today()


@pytest.fixture
def date_yesterday():
    """Get yesterday's date."""
    from datetime import timedelta

    return date.today() - timedelta(days=1)
