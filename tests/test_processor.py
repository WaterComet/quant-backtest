# tests/test_processor.py
import polars as pl
import pytest

from data.processor import DataProcessor


@pytest.fixture
def sample_raw_data() -> list[dict]:
    """Provides a small sample of raw Binance-style API data."""
    return [
        {
            "open_time": 1672531200000,  # 2023-01-01 00:00:00 UTC
            "open": "30000.50",
            "high": "30100.00",
            "low": "29900.00",
            "close": "30050.75",
            "volume": "15.5",
            "close_time": 1672534799999,
            "quote_volume": "465000.0",
            "trades": 100,
            "taker_buy_base": "5.0",
            "taker_buy_quote": "150000.0",
            "ignore": "0",
        },
        {
            "open_time": 1672534800000,  # 2023-01-01 01:00:00 UTC
            "open": "30050.75",
            "high": "30200.00",
            "low": "30000.00",
            "close": "30150.00",
            "volume": "20.0",
            "close_time": 1672538399999,
            "quote_volume": "600000.0",
            "trades": 120,
            "taker_buy_base": "8.0",
            "taker_buy_quote": "240000.0",
            "ignore": "0",
        }
    ]

def test_clean_and_typecast(sample_raw_data: list[dict]) -> None:
    """Ensures raw string/integer data is correctly cast to floats and datetimes."""
    processor = DataProcessor(data_dir="test_data")
    df = processor.clean_and_typecast(sample_raw_data)

    # 1. Check row count
    assert len(df) == 2

    # 2. Check data types (Crucial for Quant Devs)
    assert df.schema["timestamp"] == pl.Datetime
    assert df.schema["close"] == pl.Float64
    assert df.schema["volume"] == pl.Float64

    # 3. Check chronological sorting
    assert df["timestamp"][0] < df["timestamp"][1]

    # 4. Check specific value casting
    assert df["close"][0] == 30050.75

def test_empty_data_handling() -> None:
    """Ensures the processor gracefully handles empty API responses."""
    processor = DataProcessor(data_dir="test_data")
    df = processor.clean_and_typecast([])
    
    assert len(df) == 0
    assert df.schema["timestamp"] == pl.Datetime