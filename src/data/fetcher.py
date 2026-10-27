import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

class BinanceDataFetcher:
    """Fetches historical kline (candlestick) data from Binance public API."""

    BASE_URL = "https://api.binance.com/api/v3/klines"

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def _request_with_retry(
        self, session: aiohttp.ClientSession, url: str, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Executes an HTTP GET request with exponential backoff and rate limit handling."""
        for attempt in range(self.max_retries):
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return list(await response.json())
                    
                    if response.status == 429:
                        # Rate limit hit. Check for Retry-After header, else exponential backoff.
                        retry_after = int(response.headers.get("Retry-After", 0))
                        delay = retry_after if retry_after > 0 else self.base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited (429). Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                        continue

                    response.raise_for_status()

            except aiohttp.ClientError as e:
                logger.error(f"Request failed (Attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(f"Max retries exceeded for URL: {url}") from e
        
        raise RuntimeError("Unexpected exit from retry loop.")

    async def fetch_klines(
        self, symbol: str, interval: str = "1h", limit: int = 500
    ) -> list[dict[str, Any]]:
        """Fetches historical klines for a specific symbol."""
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        
        # aiohttp recommends reusing a single session for connection pooling
        async with aiohttp.ClientSession() as session:
            logger.info(f"Fetching {limit} {interval} klines for {symbol}...")
            raw_data = await self._request_with_retry(session, self.BASE_URL, params)
            
            # Map raw Binance array data to a dictionary for easier Polars ingestion
            columns = [
                "open_time", "open", "high", "low", "close", "volume", 
                "close_time", "quote_volume", "trades", "taker_buy_base", 
                "taker_buy_quote", "ignore"
            ]
            return [dict(zip(columns, candle)) for candle in raw_data]