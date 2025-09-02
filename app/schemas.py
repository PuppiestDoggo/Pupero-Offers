from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OfferCreate(BaseModel):
    title: str
    desc: str
    price: float
    seller_id: Optional[int] = 0

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None

class BidCreate(BaseModel):
    bid: float
    buyer_id: Optional[int] = 0

class OfferOut(BaseModel):
    id: str
    title: str
    desc: str
    price: float
    seller_id: int
    status: str
    timestamp: datetime

class TransactionOut(BaseModel):
    id: int
    offer_id: int
    buyer_id: int
    seller_id: int
    amount: float
    status: str
    tx_hash: str
    created_at: datetime
