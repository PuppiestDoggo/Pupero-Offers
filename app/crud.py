from typing import List, Optional
from sqlmodel import Session, select
from uuid import uuid4
from .models import Offer, Transaction

# Offer CRUD

def create_offer(session: Session, title: str, desc: str, price_xmr: float, seller_id: int = 0) -> Offer:
    offer = Offer(title=title, desc=desc, price_xmr=price_xmr, seller_id=seller_id, status="open")
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def get_offer(session: Session, offer_id: int) -> Optional[Offer]:
    return session.get(Offer, offer_id)


def list_offers(session: Session, status: Optional[str] = None) -> List[Offer]:
    stmt = select(Offer)
    if status:
        stmt = stmt.where(Offer.status == status)
    stmt = stmt.order_by(Offer.timestamp.desc())
    return list(session.exec(stmt))


def search_offers(session: Session, query: str) -> List[Offer]:
    if not query:
        return []
    q = f"%{query.lower()}%"
    stmt = select(Offer).where((Offer.title.ilike(q)) | (Offer.desc.ilike(q))).order_by(Offer.timestamp.desc())
    return list(session.exec(stmt))


def update_offer_desc(session: Session, offer: Offer, new_desc: str) -> Offer:
    offer.desc = new_desc
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def delete_offer(session: Session, offer: Offer) -> None:
    session.delete(offer)
    session.commit()


# Transactions / Bids

def create_bid(session: Session, offer: Offer, amount: float, buyer_id: int = 0) -> Transaction:
    tx = Transaction(
        offer_id=offer.id,
        buyer_id=buyer_id,
        seller_id=offer.seller_id,
        amount=amount,
        status="pending",
        tx_hash=str(uuid4()).replace("-", ""),
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


def user_history(session: Session, user_id: int) -> List[Transaction]:
    stmt = select(Transaction).where((Transaction.buyer_id == user_id) | (Transaction.seller_id == user_id)).order_by(Transaction.created_at.desc())
    return list(session.exec(stmt))
