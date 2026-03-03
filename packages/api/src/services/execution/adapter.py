from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class BrokerAdapter(ABC):
    @abstractmethod
    async def place_order(self, instrument: str, side: str, qty: int,
                          order_type: str, price: float | None,
                          trigger_price: float | None, tag: str) -> dict:
        """Place order. Returns { order_id, status, broker_ref }"""

    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict:
        """Get order status. Returns { order_id, status, filled_qty, avg_fill_price }"""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> dict:
        """Cancel order. Returns { order_id, cancelled }"""

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from broker."""

    @abstractmethod
    async def get_margins(self) -> Dict[str, Any]:
        """Get margin state. Returns { used, available, total }"""
