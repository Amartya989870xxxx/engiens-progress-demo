# In-memory storage for orders.
ORDERS = []

def save(order):
    ORDERS.append(order)
    return order

def all_orders():
    return ORDERS
