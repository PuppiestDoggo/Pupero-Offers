from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Input Schemas
class OfferCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    desc: str = Field(min_length=1, max_length=2048)
    price: float = Field(gt=0)
    seller_id: Optional[int] = 0

class OfferUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    desc: Optional[str] = Field(default=None, min_length=1, max_length=2048)
    price: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = Field(default=None, min_length=2, max_length=32)

class BidCreate(BaseModel):
    bid: float = Field(gt=0)
    buyer_id: Optional[int] = 0

# Output Schemas
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
