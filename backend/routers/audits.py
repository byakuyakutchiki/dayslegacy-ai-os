from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import AuditClient, AuditFinding
from routers.auth import require_auth

router = APIRouter(prefix="/audits", tags=["audits"])


class AuditFindingCreate(BaseModel):
    category: str
    severity: str
    title: str
    description: Optional[str] = None
    recommendation: Optional[str] = None
    potential_gain: Optional[str] = None


class AuditFindingOut(BaseModel):
    id: int
    audit_id: int
    category: str
    severity: str
    title: str
    description: Optional[str]
    recommendation: Optional[str]
    potential_gain: Optional[str]
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


class AuditClientCreate(BaseModel):
    client_name: str
    sector: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    ca_estime: Optional[str] = None
    effectif: Optional[int] = None
    patrimoine_dirigeant: Optional[str] = None
    statut: Optional[str] = "en_cours"
    score_audit: Optional[float] = 0
    resume_global: Optional[str] = None


class AuditClientOut(BaseModel):
    id: int
    client_name: str
    sector: Optional[str]
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    ca_estime: Optional[str]
    effectif: Optional[int]
    patrimoine_dirigeant: Optional[str]
    statut: str
    score_audit: float
    resume_global: Optional[str]
    created_at: Optional[str]
    findings: List[AuditFindingOut]

    class Config:
        from_attributes = True


class AuditClientListOut(BaseModel):
    id: int
    client_name: str
    sector: Optional[str]
    statut: str
    score_audit: float
    created_at: Optional[str]

    class Config:
        from_attributes = True


def _dt(v):
    return v.isoformat() if v else None


def _serialize_finding(f: AuditFinding) -> dict:
    return {
        "id": f.id,
        "audit_id": f.audit_id,
        "category": f.category,
        "severity": f.severity,
        "title": f.title,
        "description": f.description,
        "recommendation": f.recommendation,
        "potential_gain": f.potential_gain,
        "status": f.status,
        "created_at": _dt(f.created_at),
    }


def _serialize_client(c: AuditClient, with_findings: bool = False) -> dict:
    base = {
        "id": c.id,
        "client_name": c.client_name,
        "sector": c.sector,
        "contact_name": c.contact_name,
        "contact_email": c.contact_email,
        "contact_phone": c.contact_phone,
        "ca_estime": c.ca_estime,
        "effectif": c.effectif,
        "patrimoine_dirigeant": c.patrimoine_dirigeant,
        "statut": c.statut,
        "score_audit": c.score_audit,
        "resume_global": c.resume_global,
        "created_at": _dt(c.created_at),
    }
    if with_findings:
        base["findings"] = [_serialize_finding(f) for f in c.findings]
    return base


@router.get("", response_model=List[AuditClientListOut])
def list_audits(db: Session = Depends(get_db), _: str = Depends(require_auth)):
    clients = db.query(AuditClient).order_by(AuditClient.created_at.desc()).all()
    return [_serialize_client(c) for c in clients]


@router.post("", response_model=AuditClientOut)
def create_audit(data: AuditClientCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    client = AuditClient(**data.model_dump(exclude_unset=True))
    db.add(client)
    db.commit()
    db.refresh(client)
    return _serialize_client(client, with_findings=True)


@router.get("/{audit_id}", response_model=AuditClientOut)
def get_audit(audit_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    client = db.query(AuditClient).options(joinedload(AuditClient.findings)).filter(AuditClient.id == audit_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Audit introuvable")
    return _serialize_client(client, with_findings=True)


@router.put("/{audit_id}", response_model=AuditClientOut)
def update_audit(audit_id: int, data: AuditClientCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    client = db.query(AuditClient).filter(AuditClient.id == audit_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Audit introuvable")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(client, k, v)
    db.commit()
    db.refresh(client)
    return _serialize_client(client, with_findings=True)


@router.delete("/{audit_id}")
def delete_audit(audit_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    client = db.query(AuditClient).filter(AuditClient.id == audit_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Audit introuvable")
    db.query(AuditFinding).filter(AuditFinding.audit_id == audit_id).delete()
    db.delete(client)
    db.commit()
    return {"ok": True}


@router.post("/{audit_id}/findings", response_model=AuditFindingOut)
def add_finding(audit_id: int, data: AuditFindingCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    client = db.query(AuditClient).filter(AuditClient.id == audit_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Audit introuvable")
    finding = AuditFinding(audit_id=audit_id, **data.model_dump(exclude_unset=True))
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return _serialize_finding(finding)


@router.put("/{audit_id}/findings/{finding_id}", response_model=AuditFindingOut)
def update_finding(audit_id: int, finding_id: int, data: AuditFindingCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    finding = db.query(AuditFinding).filter(AuditFinding.id == finding_id, AuditFinding.audit_id == audit_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding introuvable")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(finding, k, v)
    db.commit()
    db.refresh(finding)
    return _serialize_finding(finding)


@router.delete("/{audit_id}/findings/{finding_id}")
def delete_finding(audit_id: int, finding_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    finding = db.query(AuditFinding).filter(AuditFinding.id == finding_id, AuditFinding.audit_id == audit_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding introuvable")
    db.delete(finding)
    db.commit()
    return {"ok": True}
