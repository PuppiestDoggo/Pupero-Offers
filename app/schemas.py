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
    desc: str = Field(min_length=1, max_length=2048)

class BidCreate(BaseModel):
    bid: float = Field(gt=0)
    buyer_id: Optional[int] = 0

# Output Schemas
class OfferOut(BaseModel):
    id: int
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
