import logging
from decimal import Decimal

from fastapi import Depends, FastAPI, Header, HTTPException

from app.models import Order, OrderRequest
from app.payments import PaymentError, PaymentGateway
from app.store import OrderStore

logging.basicConfig(level=logging.INFO)
app = FastAPI()
store = OrderStore()
gateway = PaymentGateway()


def get_store() -> OrderStore:
    return store


def get_gateway() -> PaymentGateway:
    return gateway


@app.post("/orders", response_model=Order, status_code=201)
def place_order(request: OrderRequest, idempotency_key: str = Header(min_length=8, max_length=64),
                orders: OrderStore = Depends(get_store), payments: PaymentGateway = Depends(get_gateway)) -> Order:
    existing = orders.find_by_key(idempotency_key)
    if existing is not None:
        return existing  # a retried request returns the original order and is not charged twice
    total = sum((item.price * item.qty for item in request.items), Decimal("0"))
    try:
        payments.charge(total, request.card_token, idempotency_key)
    except PaymentError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return orders.add(idempotency_key, request.items, total, "paid")


@app.get("/orders", response_model=list[Order])
def list_orders(orders: OrderStore = Depends(get_store)) -> list[Order]:
    return orders.all()
