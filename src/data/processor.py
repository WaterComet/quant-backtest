import polars as pl
from typing import Any

FLOAT_COLUMNS = [
    "open", "high", "low", "close", "volume", 
    "quote_volume", "taker_buy_base", 
    "taker_buy_quote",
]


def kline_response_to_parquet(kline_response: list[dict[str, Any]], parquet_path: str) -> None:
    df = pl.DataFrame(kline_response)
    df = df.cast({column: float for column in FLOAT_COLUMNS})
    df.write_parquet(parquet_path)
