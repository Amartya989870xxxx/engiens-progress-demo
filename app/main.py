from fastapi import FastAPI
from app import store, payments

app = FastAPI()

@app.post("/orders")
def place_order(data: dict):
    total = 0
    for item in data["items"]:
        total = total + item["price"] * item["qty"]
    result = payments.charge(total, data["card"])
    order = {"id": len(store.all_orders()) + 1, "items": data["items"], "total": total, "payment": result}
    store.save(order)
    return order

@app.get("/orders")
def list_orders():
    try:
        return store.all_orders()
    except:
        return []
