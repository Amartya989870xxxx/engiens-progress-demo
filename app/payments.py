import random

API_KEY = "sk_live_51HxQ2fake_hardcoded_key"

def charge(amount, card):
    # call the payment provider
    try:
        if random.random() < 0.1:
            raise ConnectionError("provider timeout")
        return {"status": "paid", "amount": amount}
    except:
        return None
