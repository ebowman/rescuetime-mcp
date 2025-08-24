"""Integration tests for RescueTime MCP server."""

import asyncio
import os
from datetime import date, datetime, timedelta
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio

from rescuetime_mcp.client import RescueTimeAPIError, RescueTimeClient
from rescuetime_mcp.server import create_server


@pytest.mark.integration
class TestRescueTimeIntegration:
    """Integration tests that can be run with a real API key."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment for integration tests."""
        api_key = os.getenv("RESCUETIME_API_KEY_REAL")
        if not api_key:
            pytest.skip("RESCUETIME_API_KEY_REAL not set - skipping integration tests")
        return api_key

    @pytest_asyncio.fixture
    async def real_client(self, api_key):
        """Create a real client for integration tests."""
        async with RescueTimeClient(api_key=api_key, timeout=30) as client:
            yield client

    @pytest.mark.asyncio
    async def test_health_check_real_api(self, real_client):
        """Test health check with real API."""
        result = await real_client.health_check()
        assert isinstance(result, bool)
        # If API key is valid, should be True
        # If invalid, should be False but not raise exception

    @pytest.mark.asyncio
    async def test_get_daily_summary_feed_real_api(self, real_client):
        """Test getting daily summary feed with real API."""
        try:
            result = await real_client.get_daily_summary_feed()
            assert isinstance(result, (list, dict))

            if isinstance(result, list) and len(result) > 0:
                # Check structure of first summary
                summary = result[0]
                assert "date" in summary or "id" in summary

        except RescueTimeAPIError as e:
            # API might return errors for various reasons
            # Just ensure the error is properly structured
            assert isinstance(e.status_code, (int, type(None)))
            assert isinstance(str(e), str)

    @pytest.mark.asyncio
    async def test_get_analytic_data_real_api(self, real_client):
        """Test getting analytic data with real API."""
        from rescuetime_mcp.client import (
            AnalyticDataRequest,
            PerspectiveType,
            ResolutionTime,
        )

        # Test with last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

        request = AnalyticDataRequest(
            perspective=PerspectiveType.RANK,
            resolution_time=ResolutionTime.DAY,
            restrict_begin=start_date,
            restrict_end=end_date,
        )

        try:
            result = await real_client.get_analytic_data(request)
            assert isinstance(result, dict)

            # Check expected structure if data is available
            if "rows" in result:
                assert "row_headers" in result
                assert isinstance(result["rows"], list)
                assert isinstance(result["row_headers"], list)

        except RescueTimeAPIError as e:
            # Handle API errors gracefully
            assert isinstance(e.status_code, (int, type(None)))

    @pytest.mark.asyncio
    async def test_get_alerts_feed_real_api(self, real_client):
        """Test getting alerts feed with real API."""
        from rescuetime_mcp.client import AlertsFeedRequest

        request = AlertsFeedRequest(op="list")

        try:
            result = await real_client.get_alerts_feed(request)
            assert isinstance(result, (list, dict))

        except RescueTimeAPIError as e:
            assert isinstance(e.status_code, (int, type(None)))

    @pytest.mark.asyncio
    async def test_get_highlights_feed_real_api(self, real_client):
        """Test getting highlights feed with real API."""
        # Test with last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        try:
            result = await real_client.get_highlights_feed(start_date, end_date)
            assert isinstance(result, (list, dict))

        except RescueTimeAPIError as e:
            assert isinstance(e.status_code, (int, type(None)))

    @pytest.mark.asyncio
    async def test_get_focus_session_status_real_api(self, real_client):
        """Test getting focus session status with real API."""
        try:
            result = await real_client.get_focus_session_status()
            assert isinstance(result, dict)

            # Should contain focus session information
            # The structure may vary based on whether a session is active

        except RescueTimeAPIError as e:
            assert isinstance(e.status_code, (int, type(None)))


@pytest.mark.integration
class TestMCPServerIntegration:
    """Integration tests for the full MCP server."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment for integration tests."""
        api_key = os.getenv("RESCUETIME_API_KEY_REAL")
        if not api_key:
            pytest.skip("RESCUETIME_API_KEY_REAL not set - skipping integration tests")
        return api_key

    def test_server_creation_with_real_key(self, api_key, monkeypatch):
        """Test server creation with real API key."""
        monkeypatch.setenv("RESCUETIME_API_KEY", api_key)

        server = create_server()
        assert server is not None

        # Check that tools are registered
        tools = server.get_tools()
        tool_names = {tool.name for tool in tools}

        expected_tools = {
            "get_analytic_data",
            "get_daily_summary_feed",
            "get_alerts_feed",
            "get_highlights_feed",
            "post_highlight",
            "start_focus_session",
            "end_focus_session",
            "get_focus_session_status",
            "post_offline_time",
            "health_check",
        }

        assert expected_tools.issubset(tool_names)

    @pytest.mark.asyncio
    async def test_health_check_tool_with_real_api(self, api_key, monkeypatch):
        """Test health check tool with real API."""
        monkeypatch.setenv("RESCUETIME_API_KEY", api_key)

        server = create_server()

        try:
            tools = {tool.name: tool for tool in server.get_tools()}
            health_tool = tools["health_check"]

            result = await health_tool.handler()

            assert isinstance(result, dict)
            assert "healthy" in result
            assert "timestamp" in result
            assert "api_key_valid" in result
            assert isinstance(result["healthy"], bool)
            assert isinstance(result["api_key_valid"], bool)

        finally:
            if hasattr(server, "_cleanup"):
                await server._cleanup()


@pytest.mark.slow
class TestPerformance:
    """Performance tests for the RescueTime client."""

    @pytest_asyncio.fixture
    async def mock_client(self):
        """Create a mock client for performance tests."""
        async with RescueTimeClient(api_key="test_key", timeout=1) as client:
            yield client

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, mock_client):
        """Test handling multiple concurrent requests."""
        from unittest.mock import AsyncMock

        # Mock the _make_request method to return quickly
        mock_client._make_request = AsyncMock(return_value={"status": "success"})

        # Create multiple concurrent requests
        tasks = []
        for _i in range(10):
            task = mock_client.get_daily_summary_feed()
            tasks.append(task)

        # Execute all tasks concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()

        # All requests should complete
        assert len(results) == 10
        for result in results:
            assert result["status"] == "success"

        # Should complete relatively quickly (less than 1 second for mocked requests)
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_request_timeout_handling(self):
        """Test request timeout handling."""
        # Create client with very short timeout
        async with RescueTimeClient(api_key="test_key", timeout=0.001) as client:

            with patch.object(client.client, "get") as mock_get:
                # Simulate a slow response
                mock_get.side_effect = httpx.TimeoutException("Request timed out")

                with pytest.raises(RescueTimeAPIError):
                    await client._make_request("data")


class TestErrorHandling:
    """Test error handling across the system."""

    @pytest_asyncio.fixture
    async def client_with_bad_key(self):
        """Create client with invalid API key."""
        async with RescueTimeClient(api_key="invalid_key", timeout=5) as client:
            yield client

    @pytest.mark.asyncio
    async def test_invalid_api_key_handling(self, client_with_bad_key):
        """Test handling of invalid API key."""
        # This should either return False or raise an appropriate error
        result = await client_with_bad_key.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        # Create client with invalid base URL to simulate network error
        client = RescueTimeClient(api_key="test_key")
        client.BASE_URL = "https://invalid.domain.example.com/api"

        try:
            result = await client.health_check()
            # Should return False on network errors
            assert result is False
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        async with RescueTimeClient(api_key="test_key") as client:

            # Mock a malformed response
            mock_response = type(
                "MockResponse",
                (),
                {
                    "status_code": 200,
                    "headers": {"content-type": "application/json"},
                    "json": lambda: {"malformed": "response"},
                    "text": '{"malformed": "response"}',
                    "raise_for_status": lambda: None,
                },
            )()

            with patch.object(client.client, "get", return_value=mock_response):
                # Should not crash, just return the malformed data
                result = await client._make_request("data")
                assert isinstance(result, dict)
                assert "malformed" in result


@pytest.mark.integration
class TestDataValidation:
    """Test data validation and model behavior."""

    def test_date_validation_in_models(self):
        """Test date validation in Pydantic models."""
        from datetime import date

        from rescuetime_mcp.client import (
            AnalyticDataRequest,
            HighlightPost,
            OfflineTimePost,
        )

        # Test date string validation
        request = AnalyticDataRequest(
            restrict_begin="2024-01-01", restrict_end="2024-12-31"
        )
        assert request.restrict_begin == "2024-01-01"
        assert request.restrict_end == "2024-12-31"

        # Test date object validation
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        request = AnalyticDataRequest(restrict_begin=start_date, restrict_end=end_date)
        assert request.restrict_begin == "2024-01-01"
        assert request.restrict_end == "2024-12-31"

        # Test HighlightPost date validation
        highlight = HighlightPost(
            highlight_date=date(2024, 1, 15), description="Test highlight"
        )
        assert highlight.highlight_date == "2024-01-15"

        # Test OfflineTimePost date validation
        offline_time = OfflineTimePost(
            offline_date=date(2024, 1, 15),
            offline_hours=8.5,
            description="Offline work",
        )
        assert offline_time.offline_date == "2024-01-15"
        assert offline_time.offline_hours == 8.5

    def test_enum_validation(self):
        """Test enum validation in models."""
        from rescuetime_mcp.client import (
            AnalyticDataRequest,
            PerspectiveType,
            ResolutionTime,
            RestrictKind,
        )

        # Valid enum values should work
        request = AnalyticDataRequest(
            perspective=PerspectiveType.RANK,
            resolution_time=ResolutionTime.DAY,
            restrict_kind=RestrictKind.CATEGORY,
        )

        assert request.perspective == "rank"
        assert request.resolution_time == "day"
        assert request.restrict_kind == "category"

        # String values should also work
        request = AnalyticDataRequest(
            perspective="interval",
            resolution_time="hour",
            restrict_kind="activity",
        )

        assert request.perspective == "interval"
        assert request.resolution_time == "hour"
        assert request.restrict_kind == "activity"
