from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Offer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, index=True)
    desc: str = Field(max_length=2048)
    price_xmr: float = Field(gt=0)
    seller_id: int = Field(default=0, index=True)
    status: str = Field(default="open", index=True, max_length=32)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    offer_id: int = Field(index=True)
    buyer_id: int = Field(default=0, index=True)
    seller_id: int = Field(default=0, index=True)
    amount: float = Field(gt=0)
    status: str = Field(default="pending", index=True, max_length=32)
    tx_hash: str = Field(index=True, unique=True, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
