from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app, get_gateway, get_store
from app.payments import PaymentError
from app.store import OrderStore

ORDER = {"items": [{"sku": "book", "price": "12.50", "qty": 2}], "card_token": "tok_visa_123"}


class FakeGateway:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.charges = 0

    def charge(self, amount, card_token, idempotency_key):
        self.charges += 1
        if self.fail:
            raise PaymentError("payment provider unavailable")
        return "ch_1"


def client(gateway: FakeGateway, store: OrderStore) -> TestClient:
    app.dependency_overrides[get_gateway] = lambda: gateway
    app.dependency_overrides[get_store] = lambda: store
    return TestClient(app)


def test_places_an_order_and_computes_the_total():
    response = client(FakeGateway(), OrderStore()).post("/orders", json=ORDER, headers={"Idempotency-Key": "key-0001"})
    assert response.status_code == 201
    assert Decimal(response.json()["total"]) == Decimal("25.00")


def test_a_retried_request_creates_one_order_and_one_charge():
    gateway, store = FakeGateway(), OrderStore()
    api = client(gateway, store)
    first = api.post("/orders", json=ORDER, headers={"Idempotency-Key": "key-0002"})
    second = api.post("/orders", json=ORDER, headers={"Idempotency-Key": "key-0002"})
    assert first.json()["id"] == second.json()["id"]
    assert len(store.all()) == 1 and gateway.charges == 1


def test_a_payment_outage_is_reported_and_no_order_is_stored():
    store = OrderStore()
    response = client(FakeGateway(fail=True), store).post("/orders", json=ORDER, headers={"Idempotency-Key": "key-0003"})
    assert response.status_code == 502
    assert store.all() == []


def test_invalid_orders_are_rejected():
    api = client(FakeGateway(), OrderStore())
    bad_qty = {**ORDER, "items": [{"sku": "book", "price": "12.50", "qty": 0}]}
    raw_card = {**ORDER, "card_token": "4242424242424242"}
    assert api.post("/orders", json=bad_qty, headers={"Idempotency-Key": "key-0004"}).status_code == 422
    assert api.post("/orders", json=raw_card, headers={"Idempotency-Key": "key-0005"}).status_code == 422
    assert api.post("/orders", json=ORDER).status_code == 422  # no idempotency key
