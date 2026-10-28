from unittest.mock import AsyncMock, MagicMock

import pytest

from data.fetcher import BinanceDataFetcher


@pytest.mark.asyncio
async def test_fetcher_handles_429_rate_limit() -> None:
    """Ensures the fetcher backs off and retries when hitting a 429 status."""
    fetcher = BinanceDataFetcher(max_retries=3, base_delay=0.01) # Fast delay for testing
    
    # Mock the aiohttp session and response
    mock_session = MagicMock()
    
    # First call returns 429, second call returns 200
    mock_response_429 = AsyncMock()
    mock_response_429.status = 429
    mock_response_429.headers = {"Retry-After": "0"}
    mock_response_429.__aenter__.return_value = mock_response_429
    
    mock_response_200 = AsyncMock()
    mock_response_200.status = 200
    mock_response_200.json.return_value = [[1, 2, 3]] # Dummy data
    mock_response_200.__aenter__.return_value = mock_response_200

    mock_session.get.side_effect = [mock_response_429, mock_response_200]

    # Execute
    result = await fetcher._request_with_retry(
        mock_session, "http://fakeurl.com", {"symbol": "BTCUSDT"}
    )

    # Assert
    assert result == [[1, 2, 3]]
    assert mock_session.get.call_count == 2 # Proves it retried after the 429