# src/strategies/base.py
from abc import ABC, abstractmethod

from engine.events import MarketEvent, SignalEvent


class Strategy(ABC):
    """Abstract base class for all trading strategies."""

    @abstractmethod
    def on_market_event(self, event: MarketEvent) -> SignalEvent | None:
        """
        Called by the Engine every time a new bar is available.
        The strategy updates its internal state here and optionally returns a SignalEvent.
        """
        pass