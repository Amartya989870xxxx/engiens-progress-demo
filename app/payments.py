import logging
from decimal import Decimal

from app.config import settings

log = logging.getLogger(__name__)


class PaymentError(Exception):
    """The provider declined or could not be reached; the order must not be stored as paid."""


class PaymentGateway:
    def __init__(self, client=None, timeout: float = settings.payment_timeout_seconds) -> None:
        self.client = client
        self.timeout = timeout

    def charge(self, amount: Decimal, card_token: str, idempotency_key: str) -> str:
        if self.client is None:
            raise PaymentError("payment provider is not configured")
        try:
            response = self.client.charge(amount=amount, token=card_token, key=idempotency_key, timeout=self.timeout)
        except (TimeoutError, ConnectionError) as error:
            log.warning("payment provider unavailable: %s", type(error).__name__)
            raise PaymentError("payment provider unavailable") from error
        if response.get("status") != "paid":
            raise PaymentError("payment declined")
        return response["charge_id"]
