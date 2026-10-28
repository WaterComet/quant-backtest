# src/data/processor.py
import logging
from pathlib import Path
from typing import Any

import polars as pl

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes raw market data into a clean, typed Polars DataFrame and saves to Parquet."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def clean_and_typecast(self, raw_data: list[dict[str, Any]]) -> pl.DataFrame:
        """
        Converts raw API JSON data into a strictly typed Polars DataFrame.
        
        Args:
            raw_data: List of dictionaries from the Binance API fetcher.
            
        Returns:
            A clean Polars DataFrame with correct data types and sorted chronologically.
        """
        if not raw_data:
            logger.warning("Received empty data. Returning empty DataFrame.")
            return pl.DataFrame(schema=self._get_schema())

        # 1. Load into Polars
        df = pl.DataFrame(raw_data)

        # 2. Select and rename only the columns we care about
        df = df.select([
            pl.col("open_time").cast(pl.Int64),
            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("close").cast(pl.Float64),
            pl.col("volume").cast(pl.Float64),
            pl.col("close_time").cast(pl.Int64),
        ])

        # 3. Convert Unix timestamps (milliseconds) to Polars Datetime
        df = df.with_columns([
            pl.col("open_time").cast(pl.Datetime(time_unit="ms")).alias("timestamp"),
            pl.col("close_time").cast(pl.Datetime(time_unit="ms")).alias("close_timestamp"),
        ]).drop(["open_time", "close_time"])

        # 4. Sort chronologically (crucial for time-series backtesting)
        df = df.sort("timestamp")

        # 5. Handle missing data (forward fill for price, zero for volume)
        # Note: In production, you might want to drop rows with nulls instead of forward-filling
        df = df.fill_null(strategy="forward")
        df = df.with_columns(pl.col("volume").fill_null(0.0))

        logger.info(f"Successfully processed {len(df)} rows of market data.")
        return df

    def save_to_parquet(self, df: pl.DataFrame, symbol: str, interval: str) -> Path:
        """
        Saves the DataFrame to a partitioned Parquet file.
        
        Args:
            df: The cleaned Polars DataFrame.
            symbol: The trading pair (e.g., "BTCUSDT").
            interval: The candlestick interval (e.g., "1h").
            
        Returns:
            The Path to the saved Parquet file.
        """
        filename = f"{symbol}_{interval}.parquet"
        filepath = self.data_dir / filename
        
        # Parquet compression is highly efficient for OHLCV data
        df.write_parquet(filepath, compression="zstd")
        logger.info(f"Data saved to {filepath}")
        
        return filepath

    @staticmethod
    def _get_schema() -> dict[str, pl.datatypes.classes.DataTypeClass]:
        """Defines the expected schema for an empty DataFrame."""
        return {
            "timestamp": pl.Datetime,
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Float64,
            "close_timestamp": pl.Datetime,
        }