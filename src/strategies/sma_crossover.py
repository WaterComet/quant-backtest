# src/strategies/sma_crossover.py
import logging
from collections import deque
from datetime import datetime

from engine.events import MarketEvent, SignalEvent
from strategies.base import Strategy

logger = logging.getLogger(__name__)

class SMACrossoverStrategy(Strategy):
    """
    Strategy state is kept strictly inside the strategy.
    The engine knows nothing about moving averages.
    """
    def __init__(self, symbol: str, fast_window: int = 10, slow_window: int = 30):
        self.symbol = symbol
        self.fast_window = fast_window
        self.slow_window = slow_window
        
        # State: Rolling windows for price history (O(1) appends/pops)
        self._fast_prices: deque[float] = deque(maxlen=fast_window)
        self._slow_prices: deque[float] = deque(maxlen=slow_window)
        
        # State: Previous signal to avoid duplicate orders
        self._current_position: str = "FLAT" 

    def on_market_event(self, event: MarketEvent) -> SignalEvent | None:
        if event.symbol != self.symbol:
            return None

        # 1. Update internal state
        self._fast_prices.append(event.close)
        self._slow_prices.append(event.close)

        # 2. Check if we have enough data to calculate indicators
        if len(self._fast_prices) < self.fast_window or len(self._slow_prices) < self.slow_window:
            return None

        # 3. Calculate indicators from state
        fast_sma = sum(self._fast_prices) / self.fast_window
        slow_sma = sum(self._slow_prices) / self.slow_window

        # 4. Generate Signal based on state
        signal = None
        if fast_sma > slow_sma and self._current_position != "LONG":
            logger.info(f"[{event.timestamp}] BUY SIGNAL: Fast SMA ({fast_sma:.2f}) > Slow SMA ({slow_sma:.2f})")
            signal = SignalEvent(timestamp=event.timestamp, symbol=self.symbol, direction="BUY")
            self._current_position = "LONG"
            
        elif fast_sma < slow_sma and self._current_position != "SHORT":
            logger.info(f"[{event.timestamp}] SELL SIGNAL: Fast SMA ({fast_sma:.2f}) < Slow SMA ({slow_sma:.2f})")
            signal = SignalEvent(timestamp=event.timestamp, symbol=self.symbol, direction="SELL")
            self._current_position = "SHORT"

        return signal