from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from database import get_db
from models import Lead
from routers.auth import require_auth

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("")
def list_leads(
    skip: int = 0,
    limit: int = 50,
    score_min: Optional[float] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    q = db.query(Lead).order_by(desc(Lead.created_at))
    if score_min is not None:
        q = q.filter(Lead.score >= score_min)
    leads = q.offset(skip).limit(limit).all()
    return [_serialize(l) for l in leads]


@router.get("/stats")
def stats(db: Session = Depends(get_db), _: str = Depends(require_auth)):
    total = db.query(Lead).count()
    chauds = db.query(Lead).filter(Lead.score >= 7).count()
    moyens = db.query(Lead).filter(Lead.score >= 4, Lead.score < 7).count()
    froids = db.query(Lead).filter(Lead.score < 4).count()
    return {"total": total, "chauds": chauds, "moyens": moyens, "froids": froids}


@router.get("/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Lead introuvable")
    return _serialize(lead, full=True)


def _serialize(l: Lead, full: bool = False) -> dict:
    base = {
        "id": l.id,
        "phone": l.phone,
        "nom": l.nom,
        "prenom": l.prenom,
        "patrimoine": l.patrimoine_estime,
        "objectif": l.objectif,
        "score": l.score,
        "resume": l.resume,
        "sms": l.sms_envoye,
        "duree": l.duree_secondes,
        "date": l.created_at.isoformat() if l.created_at else None,
    }
    if full:
        base["transcript"] = l.transcript
    return base
