# src/engine/backtest.py
import asyncio
import logging
from collections.abc import AsyncIterator

from engine.events import Event, MarketEvent, SignalEvent 
from strategies.base import Strategy

logger = logging.getLogger(__name__)

class BacktestEngine:
    """The core event loop that processes historical data bar-by-bar."""

    def __init__(self, data_iterator: AsyncIterator[MarketEvent], strategy: Strategy):
        self.data_iterator = data_iterator
        self.strategy = strategy
        self.events_queue: asyncio.Queue[Event] = asyncio.Queue()

    async def run(self) -> None:
        """Main execution loop."""
        logger.info("Starting Backtest Engine...")
        
        async for market_event in self.data_iterator:
            await self.events_queue.put(market_event)
            
            while not self.events_queue.empty():
                event = await self.events_queue.get()
                await self._process_event(event)

        logger.info("Backtest Engine finished.")

    async def _process_event(self, event: Event) -> None:
        """Routes events to the appropriate handler using isinstance for strict type narrowing."""
        
        # ✅ Mypy and Python both understand this perfectly.
        if isinstance(event, MarketEvent):
            await self._on_market_event(event)
            
        elif isinstance(event, SignalEvent):
            await self._on_signal_event(event)
            
        # You will add OrderEvent and FillEvent here later!

    async def _on_market_event(self, event: MarketEvent) -> None:
        """Passes market data to the strategy."""
        signal = self.strategy.on_market_event(event)
        if signal:
            await self.events_queue.put(signal)

    async def _on_signal_event(self, event: SignalEvent) -> None:
        """Passes signals to the Portfolio/Risk module."""
        # TODO: Pass to Portfolio.update(event)
        pass