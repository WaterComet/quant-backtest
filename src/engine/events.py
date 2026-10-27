# src/engine/events.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

class EventType(Enum):
    MARKET = auto()
    SIGNAL = auto()
    ORDER = auto()
    FILL = auto()

@dataclass
class Event:
    event_type: EventType
    timestamp: datetime

@dataclass
class MarketEvent(Event):
    """Emitted when new bar data is available."""
    event_type: EventType = field(default=EventType.MARKET, kw_only=True)
    symbol: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0

@dataclass
class SignalEvent(Event):
    """Emitted by the strategy when a trade condition is met."""
    event_type: EventType = field(default=EventType.SIGNAL, kw_only=True)
    symbol: str = ""
    direction: str = "BUY" # or "SELL"
    strength: float = 1.0  # Confidence level or position sizing multiplier

@dataclass
class OrderEvent(Event):
    """Emitted by the Portfolio/Risk module to send to the execution handler."""
    event_type: EventType = field(default=EventType.ORDER, kw_only=True)
    symbol: str = ""
    order_type: str = "MARKET"
    direction: str = "BUY"
    quantity: float = 0.0

@dataclass
class FillEvent(Event):
    """Emitted by the execution handler to update the portfolio."""
    event_type: EventType = field(default=EventType.FILL, kw_only=True)
    symbol: str = ""
    quantity: float = 0.0
    fill_price: float = 0.0
    commission: float = 0.0