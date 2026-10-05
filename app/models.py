from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class Item(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    qty: int = Field(gt=0, le=100)


class OrderRequest(BaseModel):
    items: list[Item] = Field(min_length=1, max_length=50)
    card_token: str = Field(min_length=8, max_length=128)

    @field_validator("card_token")
    @classmethod
    def no_raw_card_numbers(cls, value: str) -> str:
        if value.replace(" ", "").isdigit():
            raise ValueError("send a tokenised card, never a raw card number")
        return value


class Order(BaseModel):
    id: int
    items: list[Item]
    total: Decimal
    status: str
