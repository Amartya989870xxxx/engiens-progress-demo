# Orders service

A small FastAPI service that places and lists customer orders.

- Requests are validated (items, quantities, prices, tokenised cards only).
- `POST /orders` needs an `Idempotency-Key` header: a retried request returns the original order and is charged once.
- Payment failures return `502` and never store an unpaid order; the provider key comes from `PAYMENT_API_KEY`.

Run: `pip install -r requirements.txt && uvicorn app.main:app --reload`
Test: `pytest`
