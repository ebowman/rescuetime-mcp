"""Tests for RescueTime API client."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from rescuetime_mcp.client import (
    AnalyticDataRequest,
    DailySummaryRequest,
    HighlightPost,
    OfflineTimePost,
    PerspectiveType,
    RescueTimeAPIError,
    RescueTimeClient,
    ResolutionTime,
)


class TestRescueTimeClient:
    """Test cases for RescueTimeClient."""

    @pytest_asyncio.fixture
    async def client(self, mock_api_key):
        """Create a real client instance for testing."""
        client = RescueTimeClient(api_key=mock_api_key, timeout=10)
        yield client
        await client.close()

    def test_init(self, mock_api_key):
        """Test client initialization."""
        client = RescueTimeClient(api_key=mock_api_key, timeout=15)
        assert client.api_key == mock_api_key
        assert client.timeout == 15
        assert client.BASE_URL == "https://www.rescuetime.com/anapi"

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_api_key):
        """Test client as async context manager."""
        async with RescueTimeClient(api_key=mock_api_key) as client:
            assert isinstance(client, RescueTimeClient)
            assert client.api_key == mock_api_key

    @pytest.mark.asyncio
    async def test_make_request_success(self, client, mock_httpx_response):
        """Test successful API request."""
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_httpx_response

            result = await client._make_request("data", params={"test": "value"})

            assert result == {"status": "success"}
            mock_get.assert_called_once()

            # Check that API key was added to params
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["key"] == client.api_key
            assert params["format"] == "json"
            assert params["test"] == "value"

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, client):
        """Test API request with HTTP error."""
        error_response = MagicMock()
        error_response.status_code = 401
        error_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError(
            message="Unauthorized", request=MagicMock(), response=error_response
        )

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = http_error

            with pytest.raises(RescueTimeAPIError) as exc_info:
                await client._make_request("data")

            assert "HTTP 401 error" in str(exc_info.value)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """Test API request with network error."""
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Network error")

            with pytest.raises(RescueTimeAPIError) as exc_info:
                await client._make_request("data")

            assert "Request error" in str(exc_info.value)
            assert exc_info.value.status_code is None

    @pytest.mark.asyncio
    async def test_get_analytic_data(self, client, sample_analytic_data):
        """Test getting analytic data."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_analytic_data

            request = AnalyticDataRequest(
                perspective=PerspectiveType.RANK,
                resolution_time=ResolutionTime.DAY,
                restrict_begin="2024-01-01",
                restrict_end="2024-01-31",
            )

            result = await client.get_analytic_data(request)

            assert result == sample_analytic_data
            mock_request.assert_called_once_with(
                "data",
                params={
                    "perspective": "rank",
                    "resolution_time": "day",
                    "restrict_begin": "2024-01-01",
                    "restrict_end": "2024-01-31",
                },
            )

    @pytest.mark.asyncio
    async def test_get_daily_summary_feed(self, client, sample_daily_summary):
        """Test getting daily summary feed."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_daily_summary

            result = await client.get_daily_summary_feed()

            assert result == sample_daily_summary
            mock_request.assert_called_once_with("daily_summary_feed", params={})

    @pytest.mark.asyncio
    async def test_get_daily_summary_feed_with_dates(
        self, client, sample_daily_summary
    ):
        """Test getting daily summary feed with date restrictions."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_daily_summary

            request = DailySummaryRequest(
                restrict_begin="2024-01-01", restrict_end="2024-01-31"
            )

            result = await client.get_daily_summary_feed(request)

            assert result == sample_daily_summary
            mock_request.assert_called_once_with(
                "daily_summary_feed",
                params={
                    "restrict_begin": "2024-01-01",
                    "restrict_end": "2024-01-31",
                },
            )

    @pytest.mark.asyncio
    async def test_get_alerts_feed(self, client, sample_alerts):
        """Test getting alerts feed."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_alerts

            result = await client.get_alerts_feed()

            assert result == sample_alerts
            mock_request.assert_called_once_with("alerts_feed", params={"op": "list"})

    @pytest.mark.asyncio
    async def test_dismiss_alert(self, client):
        """Test dismissing an alert."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "dismissed"}

            result = await client.dismiss_alert(123)

            assert result == {"status": "dismissed"}
            mock_request.assert_called_once_with(
                "alerts_feed", params={"op": "dismiss", "id": 123}
            )

    @pytest.mark.asyncio
    async def test_get_highlights_feed(self, client, sample_highlights):
        """Test getting highlights feed."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_highlights

            result = await client.get_highlights_feed("2024-01-01", "2024-01-31")

            assert result == sample_highlights
            mock_request.assert_called_once_with(
                "highlights_feed",
                params={
                    "restrict_begin": "2024-01-01",
                    "restrict_end": "2024-01-31",
                },
            )

    @pytest.mark.asyncio
    async def test_get_highlights_feed_with_date_objects(
        self, client, sample_highlights
    ):
        """Test getting highlights feed with date objects."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_highlights

            start_date = date(2024, 1, 1)
            end_date = date(2024, 1, 31)

            result = await client.get_highlights_feed(start_date, end_date)

            assert result == sample_highlights
            mock_request.assert_called_once_with(
                "highlights_feed",
                params={
                    "restrict_begin": "2024-01-01",
                    "restrict_end": "2024-01-31",
                },
            )

    @pytest.mark.asyncio
    async def test_post_highlight(self, client):
        """Test posting a highlight."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "created"}

            highlight = HighlightPost(
                highlight_date="2024-01-15", description="Test highlight", source="test"
            )

            result = await client.post_highlight(highlight)

            assert result == {"status": "created"}
            mock_request.assert_called_once_with(
                "highlights_post",
                method="POST",
                data={
                    "highlight_date": "2024-01-15",
                    "description": "Test highlight",
                    "source": "test",
                },
            )

    @pytest.mark.asyncio
    async def test_start_focus_session(self, client):
        """Test starting a focus session."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "started"}

            result = await client.start_focus_session(90)

            assert result == {"status": "started"}
            mock_request.assert_called_once_with(
                "start_focustime", method="POST", data={"duration": 90}
            )

    @pytest.mark.asyncio
    async def test_start_focus_session_no_duration(self, client):
        """Test starting a focus session without duration."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "started"}

            result = await client.start_focus_session()

            assert result == {"status": "started"}
            mock_request.assert_called_once_with(
                "start_focustime", method="POST", data={}
            )

    @pytest.mark.asyncio
    async def test_end_focus_session(self, client):
        """Test ending a focus session."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "ended"}

            result = await client.end_focus_session()

            assert result == {"status": "ended"}
            mock_request.assert_called_once_with("end_focustime", method="POST")

    @pytest.mark.asyncio
    async def test_get_focus_session_status(self, client, sample_focus_status):
        """Test getting focus session status."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = sample_focus_status

            result = await client.get_focus_session_status()

            assert result == sample_focus_status
            mock_request.assert_called_once_with("focustime_status")

    @pytest.mark.asyncio
    async def test_post_offline_time(self, client):
        """Test posting offline time."""
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "posted"}

            offline_time = OfflineTimePost(
                offline_date="2024-01-15", offline_hours=4.5, description="Offline work"
            )

            result = await client.post_offline_time(offline_time)

            assert result == {"status": "posted"}
            mock_request.assert_called_once_with(
                "offline_time_post",
                method="POST",
                data={
                    "offline_date": "2024-01-15",
                    "offline_hours": 4.5,
                    "description": "Offline work",
                },
            )

    @pytest.mark.asyncio
    async def test_health_check_success(self, client, sample_daily_summary):
        """Test successful health check."""
        with patch.object(
            client, "get_daily_summary_feed", new_callable=AsyncMock
        ) as mock_feed:
            mock_feed.return_value = sample_daily_summary

            result = await client.health_check()

            assert result is True
            mock_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test failed health check."""
        with patch.object(
            client, "get_daily_summary_feed", new_callable=AsyncMock
        ) as mock_feed:
            mock_feed.side_effect = RescueTimeAPIError("API Error")

            result = await client.health_check()

            assert result is False
            mock_feed.assert_called_once()


class TestDataModels:
    """Test cases for data models."""

    def test_analytic_data_request(self):
        """Test AnalyticDataRequest model."""
        request = AnalyticDataRequest(
            perspective=PerspectiveType.RANK,
            resolution_time=ResolutionTime.DAY,
            restrict_begin="2024-01-01",
            restrict_end="2024-01-31",
        )

        assert request.perspective == "rank"
        assert request.resolution_time == "day"
        assert request.restrict_begin == "2024-01-01"
        assert request.restrict_end == "2024-01-31"

    def test_analytic_data_request_with_date_objects(self):
        """Test AnalyticDataRequest with date objects."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        request = AnalyticDataRequest(
            restrict_begin=start_date,
            restrict_end=end_date,
        )

        assert request.restrict_begin == "2024-01-01"
        assert request.restrict_end == "2024-01-31"

    def test_highlight_post(self):
        """Test HighlightPost model."""
        highlight = HighlightPost(
            highlight_date="2024-01-15",
            description="Test highlight",
            source="test_source",
        )

        assert highlight.highlight_date == "2024-01-15"
        assert highlight.description == "Test highlight"
        assert highlight.source == "test_source"

    def test_highlight_post_with_date_object(self):
        """Test HighlightPost with date object."""
        test_date = date(2024, 1, 15)

        highlight = HighlightPost(
            highlight_date=test_date, description="Test highlight"
        )

        assert highlight.highlight_date == "2024-01-15"

    def test_offline_time_post(self):
        """Test OfflineTimePost model."""
        offline_time = OfflineTimePost(
            offline_date="2024-01-15", offline_hours=4.5, description="Offline work"
        )

        assert offline_time.offline_date == "2024-01-15"
        assert offline_time.offline_hours == 4.5
        assert offline_time.description == "Offline work"

    def test_offline_time_post_with_date_object(self):
        """Test OfflineTimePost with date object."""
        test_date = date(2024, 1, 15)

        offline_time = OfflineTimePost(
            offline_date=test_date, offline_hours=8, description="Full day offline"
        )

        assert offline_time.offline_date == "2024-01-15"


class TestRescueTimeAPIError:
    """Test cases for RescueTimeAPIError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = RescueTimeAPIError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = RescueTimeAPIError("Not found", status_code=404)
        assert str(error) == "Not found"
        assert error.status_code == 404

    def test_error_with_response_data(self):
        """Test error with response data."""
        response_data = {"error": "Invalid API key"}
        error = RescueTimeAPIError(
            "Unauthorized", status_code=401, response_data=response_data
        )

        assert str(error) == "Unauthorized"
        assert error.status_code == 401
        assert error.response_data == response_data
