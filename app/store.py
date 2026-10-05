import threading
from decimal import Decimal

from app.models import Item, Order


class OrderStore:
    """In-memory store. Placing an order is idempotent per key, so a retried request can't create a second order."""

    def __init__(self) -> None:
        self._orders: list[Order] = []
        self._by_key: dict[str, Order] = {}
        self._lock = threading.Lock()

    def find_by_key(self, key: str) -> Order | None:
        with self._lock:
            return self._by_key.get(key)

    def add(self, key: str, items: list[Item], total: Decimal, status: str) -> Order:
        with self._lock:
            existing = self._by_key.get(key)
            if existing is not None:
                return existing
            order = Order(id=len(self._orders) + 1, items=items, total=total, status=status)
            self._orders.append(order)
            self._by_key[key] = order
            return order

    def all(self) -> list[Order]:
        with self._lock:
            return list(self._orders)
