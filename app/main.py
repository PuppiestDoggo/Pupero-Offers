from fastapi import FastAPI, Depends, HTTPException, status, Form, Body, Request, Query
from typing import List, Optional
from sqlmodel import Session
from .database import get_session, init_db
from .schemas import OfferCreate, OfferUpdate, BidCreate, OfferOut, TransactionOut
from .crud import create_offer, get_offer_by_public_id, list_offers, search_offers, update_offer_fields, delete_offer, create_bid, user_history
from .models import Offer as OfferModel, Transaction as TransactionModel

app = FastAPI(title="Pupero Offers Service")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# Helpers to map model to output schema

def _offer_to_out(m: OfferModel) -> OfferOut:
    return OfferOut(
        id=m.public_id,
        title=m.title,
        desc=m.desc,
        price=m.price_xmr,
        seller_id=m.seller_id,
        status=m.status,
        timestamp=m.timestamp,
    )


def _tx_to_out(t: TransactionModel) -> TransactionOut:
    return TransactionOut(
        id=t.id,
        offer_id=t.offer_id,
        buyer_id=t.buyer_id,
        seller_id=t.seller_id,
        amount=t.amount,
        status=t.status,
        tx_hash=t.tx_hash,
        created_at=t.created_at,
    )


# Endpoints per spec

@app.get("/offers", response_model=List[OfferOut])
def api_list_offers(status: Optional[str] = Query(default=None), session: Session = Depends(get_session)):
    offers = list_offers(session, status=status)
    return [_offer_to_out(o) for o in offers]


@app.post("/offers")
def api_create_offer(payload: OfferCreate, session: Session = Depends(get_session)):
    offer = create_offer(session, title=payload.title, desc=payload.desc, price_xmr=payload.price, seller_id=payload.seller_id or 0)
    return {"id": offer.public_id}


@app.get("/offers/{offer_id}", response_model=OfferOut)
def api_offer_details(offer_id: str, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return _offer_to_out(offer)


@app.put("/offers/{offer_id}")
def api_update_offer(offer_id: str, payload: OfferUpdate, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    updated = update_offer_fields(session, offer, title=payload.title, desc=payload.desc, price_xmr=payload.price, status=payload.status)
    return {"message": "updated", "id": updated.public_id}


@app.delete("/offers/{offer_id}")
def api_delete_offer(offer_id: str, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    delete_offer(session, offer)
    return {"message": "deleted"}


@app.get("/offers/search", response_model=List[OfferOut])
def api_search_offers(query: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    offers = search_offers(session, query=query)
    return [_offer_to_out(o) for o in offers]


@app.post("/offers/{offer_id}/bid")
def api_bid_offer(offer_id: str, payload: BidCreate, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    # Prevent self-trade bids
    buyer_id = int(payload.buyer_id or 0)
    if buyer_id and offer.seller_id and int(offer.seller_id) == buyer_id:
        raise HTTPException(status_code=400, detail="Cannot bid on your own offer")
    tx = create_bid(session, offer, amount=payload.bid, buyer_id=buyer_id)
    return {"tx_id": tx.tx_hash}


@app.get("/offers/history", response_model=List[TransactionOut])
def api_offers_history(user_id: int = Query(..., ge=0), session: Session = Depends(get_session)):
    txs = user_history(session, user_id=user_id)
    return [_tx_to_out(t) for t in txs]


# Basic health for convenience
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Alias for k8s/monitoring expectations
@app.get("/health")
def health():
    return {"status": "ok"}
