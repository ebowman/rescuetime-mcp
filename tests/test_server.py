"""Tests for RescueTime MCP server."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from rescuetime_mcp.client import RescueTimeAPIError
from rescuetime_mcp.server import create_server, main


class TestCreateServer:
    """Test cases for server creation."""

    def test_create_server_with_env_var(self, monkeypatch):
        """Test server creation with environment variable."""
        monkeypatch.setenv("RESCUETIME_API_KEY", "test_key_123")

        server = create_server()

        assert server is not None
        assert hasattr(server, "_cleanup")

    def test_create_server_with_default_key(self, monkeypatch):
        """Test server creation with default API key."""
        monkeypatch.delenv("RESCUETIME_API_KEY", raising=False)

        server = create_server()

        assert server is not None

    def test_create_server_no_api_key(self, monkeypatch):
        """Test server creation fails without API key."""
        monkeypatch.delenv("RESCUETIME_API_KEY", raising=False)

        # Mock the default key to be None
        with patch("rescuetime_mcp.server.os.getenv", return_value=None):
            with pytest.raises(
                ValueError, match="RESCUETIME_API_KEY environment variable is required"
            ):
                create_server()


class TestMCPTools:
    """Test cases for MCP tools."""

    @pytest_asyncio.fixture
    async def server_with_mock_client(self, monkeypatch):
        """Create server with mocked client."""
        monkeypatch.setenv("RESCUETIME_API_KEY", "test_key")

        mock_client = MagicMock()
        mock_client.get_analytic_data = AsyncMock()
        mock_client.get_daily_summary_feed = AsyncMock()
        mock_client.get_alerts_feed = AsyncMock()
        mock_client.dismiss_alert = AsyncMock()
        mock_client.get_highlights_feed = AsyncMock()
        mock_client.post_highlight = AsyncMock()
        mock_client.start_focus_session = AsyncMock()
        mock_client.end_focus_session = AsyncMock()
        mock_client.get_focus_session_status = AsyncMock()
        mock_client.post_offline_time = AsyncMock()
        mock_client.health_check = AsyncMock()
        mock_client.close = AsyncMock()

        server = create_server()

        # Patch the client creation
        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            yield server, mock_client

        await server._cleanup()

    @pytest.mark.asyncio
    async def test_get_analytic_data_tool(
        self, server_with_mock_client, sample_analytic_data
    ):
        """Test get_analytic_data tool."""
        server, mock_client = server_with_mock_client
        mock_client.get_analytic_data.return_value = sample_analytic_data

        # Get the tool function
        tools = {tool.name: tool for tool in server.get_tools()}
        get_analytic_data_tool = tools["get_analytic_data"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await get_analytic_data_tool.handler(
                perspective="rank",
                resolution_time="day",
                restrict_begin="2024-01-01",
                restrict_end="2024-01-31",
            )

        assert result == sample_analytic_data
        mock_client.get_analytic_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analytic_data_tool_error(self, server_with_mock_client):
        """Test get_analytic_data tool with error."""
        server, mock_client = server_with_mock_client
        mock_client.get_analytic_data.side_effect = RescueTimeAPIError("API Error")

        tools = {tool.name: tool for tool in server.get_tools()}
        get_analytic_data_tool = tools["get_analytic_data"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            with pytest.raises(RuntimeError, match="Failed to get analytic data"):
                await get_analytic_data_tool.handler()

    @pytest.mark.asyncio
    async def test_get_daily_summary_feed_tool(
        self, server_with_mock_client, sample_daily_summary
    ):
        """Test get_daily_summary_feed tool."""
        server, mock_client = server_with_mock_client
        mock_client.get_daily_summary_feed.return_value = sample_daily_summary

        tools = {tool.name: tool for tool in server.get_tools()}
        daily_summary_tool = tools["get_daily_summary_feed"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await daily_summary_tool.handler(
                restrict_begin="2024-01-01", restrict_end="2024-01-31"
            )

        assert result == sample_daily_summary
        mock_client.get_daily_summary_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_daily_summary_feed_tool_no_params(
        self, server_with_mock_client, sample_daily_summary
    ):
        """Test get_daily_summary_feed tool without parameters."""
        server, mock_client = server_with_mock_client
        mock_client.get_daily_summary_feed.return_value = sample_daily_summary

        tools = {tool.name: tool for tool in server.get_tools()}
        daily_summary_tool = tools["get_daily_summary_feed"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await daily_summary_tool.handler()

        assert result == sample_daily_summary
        # Should be called with None request
        mock_client.get_daily_summary_feed.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_get_alerts_feed_tool(self, server_with_mock_client, sample_alerts):
        """Test get_alerts_feed tool."""
        server, mock_client = server_with_mock_client
        mock_client.get_alerts_feed.return_value = sample_alerts

        tools = {tool.name: tool for tool in server.get_tools()}
        alerts_tool = tools["get_alerts_feed"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await alerts_tool.handler(op="list")

        assert result == sample_alerts
        mock_client.get_alerts_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_dismiss_alert_tool(self, server_with_mock_client):
        """Test dismiss_alert tool."""
        server, mock_client = server_with_mock_client
        mock_client.dismiss_alert.return_value = {"status": "dismissed"}

        tools = {tool.name: tool for tool in server.get_tools()}
        dismiss_alert_tool = tools["dismiss_alert"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await dismiss_alert_tool.handler(alert_id=123)

        assert result == {"status": "dismissed"}
        mock_client.dismiss_alert.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_highlights_feed_tool(
        self, server_with_mock_client, sample_highlights
    ):
        """Test get_highlights_feed tool."""
        server, mock_client = server_with_mock_client
        mock_client.get_highlights_feed.return_value = sample_highlights

        tools = {tool.name: tool for tool in server.get_tools()}
        highlights_tool = tools["get_highlights_feed"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await highlights_tool.handler(
                restrict_begin="2024-01-01", restrict_end="2024-01-31"
            )

        assert result == sample_highlights
        mock_client.get_highlights_feed.assert_called_once_with(
            "2024-01-01", "2024-01-31"
        )

    @pytest.mark.asyncio
    async def test_post_highlight_tool(self, server_with_mock_client):
        """Test post_highlight tool."""
        server, mock_client = server_with_mock_client
        mock_client.post_highlight.return_value = {"status": "created"}

        tools = {tool.name: tool for tool in server.get_tools()}
        post_highlight_tool = tools["post_highlight"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await post_highlight_tool.handler(
                highlight_date="2024-01-15", description="Test highlight", source="test"
            )

        assert result == {"status": "created"}
        mock_client.post_highlight.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_focus_session_tool(self, server_with_mock_client):
        """Test start_focus_session tool."""
        server, mock_client = server_with_mock_client
        mock_client.start_focus_session.return_value = {"status": "started"}

        tools = {tool.name: tool for tool in server.get_tools()}
        start_focus_tool = tools["start_focus_session"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await start_focus_tool.handler(duration=90)

        assert result == {"status": "started"}
        mock_client.start_focus_session.assert_called_once_with(90)

    @pytest.mark.asyncio
    async def test_start_focus_session_tool_no_duration(self, server_with_mock_client):
        """Test start_focus_session tool without duration."""
        server, mock_client = server_with_mock_client
        mock_client.start_focus_session.return_value = {"status": "started"}

        tools = {tool.name: tool for tool in server.get_tools()}
        start_focus_tool = tools["start_focus_session"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await start_focus_tool.handler()

        assert result == {"status": "started"}
        mock_client.start_focus_session.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_end_focus_session_tool(self, server_with_mock_client):
        """Test end_focus_session tool."""
        server, mock_client = server_with_mock_client
        mock_client.end_focus_session.return_value = {"status": "ended"}

        tools = {tool.name: tool for tool in server.get_tools()}
        end_focus_tool = tools["end_focus_session"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await end_focus_tool.handler()

        assert result == {"status": "ended"}
        mock_client.end_focus_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_focus_session_status_tool(
        self, server_with_mock_client, sample_focus_status
    ):
        """Test get_focus_session_status tool."""
        server, mock_client = server_with_mock_client
        mock_client.get_focus_session_status.return_value = sample_focus_status

        tools = {tool.name: tool for tool in server.get_tools()}
        status_tool = tools["get_focus_session_status"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await status_tool.handler()

        assert result == sample_focus_status
        mock_client.get_focus_session_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_offline_time_tool(self, server_with_mock_client):
        """Test post_offline_time tool."""
        server, mock_client = server_with_mock_client
        mock_client.post_offline_time.return_value = {"status": "posted"}

        tools = {tool.name: tool for tool in server.get_tools()}
        offline_time_tool = tools["post_offline_time"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await offline_time_tool.handler(
                offline_date="2024-01-15", offline_hours=4.5, description="Offline work"
            )

        assert result == {"status": "posted"}
        mock_client.post_offline_time.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_tool_success(self, server_with_mock_client):
        """Test health_check tool success."""
        server, mock_client = server_with_mock_client
        mock_client.health_check.return_value = True

        tools = {tool.name: tool for tool in server.get_tools()}
        health_tool = tools["health_check"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await health_tool.handler()

        assert result["healthy"] is True
        assert result["api_key_valid"] is True
        assert "timestamp" in result
        mock_client.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_tool_failure(self, server_with_mock_client):
        """Test health_check tool failure."""
        server, mock_client = server_with_mock_client
        mock_client.health_check.return_value = False

        tools = {tool.name: tool for tool in server.get_tools()}
        health_tool = tools["health_check"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await health_tool.handler()

        assert result["healthy"] is False
        assert result["api_key_valid"] is False
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_check_tool_exception(self, server_with_mock_client):
        """Test health_check tool with exception."""
        server, mock_client = server_with_mock_client
        mock_client.health_check.side_effect = Exception("Network error")

        tools = {tool.name: tool for tool in server.get_tools()}
        health_tool = tools["health_check"]

        with patch("rescuetime_mcp.client.RescueTimeClient", return_value=mock_client):
            result = await health_tool.handler()

        assert result["healthy"] is False
        assert "timestamp" in result
        assert result["error"] == "Network error"


class TestMain:
    """Test cases for main function."""

    def test_main_version(self, monkeypatch, capsys):
        """Test main function with --version flag."""
        monkeypatch.setattr("sys.argv", ["rescuetime-mcp", "--version"])

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "rescuetime-mcp 0.1.0" in captured.out

    def test_main_keyboard_interrupt(self, monkeypatch):
        """Test main function handles KeyboardInterrupt."""
        monkeypatch.setenv("RESCUETIME_API_KEY", "test_key")

        with patch("rescuetime_mcp.server.create_server") as mock_create:
            mock_server = MagicMock()
            mock_server.run.side_effect = KeyboardInterrupt()
            mock_create.return_value = mock_server

            # Should not raise, just exit gracefully
            main()

            mock_create.assert_called_once()
            mock_server.run.assert_called_once()

    def test_main_server_error(self, monkeypatch):
        """Test main function handles server errors."""
        monkeypatch.setenv("RESCUETIME_API_KEY", "test_key")

        with patch("rescuetime_mcp.server.create_server") as mock_create:
            mock_server = MagicMock()
            mock_server.run.side_effect = Exception("Server error")
            mock_create.return_value = mock_server

            with pytest.raises(Exception, match="Server error"):
                main()

    def test_main_no_args(self, monkeypatch):
        """Test main function with no arguments."""
        monkeypatch.setattr("sys.argv", ["rescuetime-mcp"])
        monkeypatch.setenv("RESCUETIME_API_KEY", "test_key")

        with patch("rescuetime_mcp.server.create_server") as mock_create:
            mock_server = MagicMock()
            mock_server.run.side_effect = KeyboardInterrupt()  # To exit cleanly
            mock_create.return_value = mock_server

            main()

            mock_create.assert_called_once()
            mock_server.run.assert_called_once()
