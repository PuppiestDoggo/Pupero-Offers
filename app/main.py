from fastapi import FastAPI, Depends, HTTPException, status, Form, Body, Request, Query
from typing import List, Optional
from sqlmodel import Session
import logging
import json
import time
from datetime import datetime
from .database import get_session, init_db
from .schemas import OfferCreate, OfferUpdate, BidCreate, OfferOut, TransactionOut
from .crud import create_offer, get_offer_by_public_id, list_offers, search_offers, update_offer_fields, delete_offer, create_bid, user_history
from .models import Offer as OfferModel, Transaction as TransactionModel

# Logger setup
logger = logging.getLogger("pupero_offers")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    # Stdout handler
    stdout_handler = logging.StreamHandler()
    logger.addHandler(stdout_handler)
    # Optional File handler
    import os
    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            from logging import FileHandler
            file_handler = FileHandler(log_file)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(json.dumps({"event": "file_logging_setup_failed", "error": str(e)}))

app = FastAPI(title="Pupero Offers Service")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = int((time.time() - start_time) * 1000)
    
    log_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "http_request",
        "service": "offers",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": duration,
        "client": request.client.host if request.client else None,
    }
    logger.info(json.dumps(log_record))
    return response

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
    logger.info(json.dumps({"event": "offers_list", "status_filter": status, "count": len(offers)}))
    return [_offer_to_out(o) for o in offers]


@app.post("/offers")
def api_create_offer(payload: OfferCreate, session: Session = Depends(get_session)):
    offer = create_offer(session, title=payload.title, desc=payload.desc, price_xmr=payload.price, seller_id=payload.seller_id or 0)
    logger.info(json.dumps({
        "event": "offer_created", 
        "offer_id": offer.public_id, 
        "seller_id": offer.seller_id,
        "title": offer.title,
        "price_xmr": offer.price_xmr
    }))
    return {"id": offer.public_id}


@app.get("/offers/{offer_id}", response_model=OfferOut)
def api_offer_details(offer_id: str, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        logger.info(json.dumps({"event": "offer_not_found", "offer_id": offer_id}))
        raise HTTPException(status_code=404, detail="Offer not found")
    logger.info(json.dumps({"event": "offer_details", "offer_id": offer_id, "seller_id": offer.seller_id}))
    return _offer_to_out(offer)


@app.put("/offers/{offer_id}")
def api_update_offer(offer_id: str, payload: OfferUpdate, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        logger.info(json.dumps({"event": "offer_not_found_update", "offer_id": offer_id}))
        raise HTTPException(status_code=404, detail="Offer not found")
    updated = update_offer_fields(session, offer, title=payload.title, desc=payload.desc, price_xmr=payload.price, status=payload.status)
    logger.info(json.dumps({"event": "offer_updated", "offer_id": updated.public_id, "status": updated.status}))
    return {"message": "updated", "id": updated.public_id}


@app.delete("/offers/{offer_id}")
def api_delete_offer(offer_id: str, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        logger.info(json.dumps({"event": "offer_not_found_delete", "offer_id": offer_id}))
        raise HTTPException(status_code=404, detail="Offer not found")
    delete_offer(session, offer)
    logger.info(json.dumps({"event": "offer_deleted", "offer_id": offer_id}))
    return {"message": "deleted"}


@app.get("/offers/search", response_model=List[OfferOut])
def api_search_offers(query: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    offers = search_offers(session, query=query)
    logger.info(json.dumps({"event": "offer_search", "query": query, "results_count": len(offers)}))
    return [_offer_to_out(o) for o in offers]


@app.post("/offers/{offer_id}/bid")
def api_bid_offer(offer_id: str, payload: BidCreate, session: Session = Depends(get_session)):
    offer = get_offer_by_public_id(session, offer_id)
    if not offer:
        logger.info(json.dumps({"event": "bid_failed_offer_not_found", "offer_id": offer_id}))
        raise HTTPException(status_code=404, detail="Offer not found")
    # Prevent self-trade bids
    buyer_id = int(payload.buyer_id or 0)
    if buyer_id and offer.seller_id and int(offer.seller_id) == buyer_id:
        logger.info(json.dumps({"event": "bid_failed_self_trade", "offer_id": offer_id, "buyer_id": buyer_id}))
        raise HTTPException(status_code=400, detail="Cannot bid on your own offer")
    tx = create_bid(session, offer, amount=payload.bid, buyer_id=buyer_id)
    logger.info(json.dumps({"event": "bid_placed", "offer_id": offer_id, "buyer_id": buyer_id, "amount": payload.bid, "tx_id": tx.tx_hash}))
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
