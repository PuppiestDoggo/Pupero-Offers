from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Offer(SQLModel, table=True):
    __tablename__ = "offer"
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(index=True)
    title: str = Field(index=True)
    desc: str
    price_xmr: float
    seller_id: int = Field(default=0, index=True)
    status: str = Field(default="open", index=True)
    timestamp: Optional[datetime] = Field(default=None, index=True)

class Transaction(SQLModel, table=True):
    __tablename__ = "transaction"
    id: Optional[int] = Field(default=None, primary_key=True)
    offer_id: int = Field(index=True)
    buyer_id: int = Field(default=0, index=True)
    seller_id: int = Field(default=0, index=True)
    amount: float
    status: str = Field(default="pending", index=True)
    tx_hash: str = Field(index=True)
    created_at: Optional[datetime] = Field(default=None, index=True)
