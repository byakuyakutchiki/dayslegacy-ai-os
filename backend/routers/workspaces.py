from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import Workspace, WorkspaceMember
from routers.auth import require_auth

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# ══════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════

class WorkspaceCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    plan: Optional[str] = "demo"
    branding_primary: Optional[str] = "#CC9B12"
    branding_secondary: Optional[str] = "#0b0b0c"
    logo_url: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    branding_primary: Optional[str] = None
    branding_secondary: Optional[str] = None
    logo_url: Optional[str] = None


class WorkspaceMemberCreate(BaseModel):
    user_email: str
    role: Optional[str] = "bd"
    display_name: Optional[str] = None


class WorkspaceMemberUpdate(BaseModel):
    role: Optional[str] = None
    display_name: Optional[str] = None
    is_online: Optional[bool] = None


class WorkspaceOut(BaseModel):
    id: int
    name: str
    slug: str
    owner_email: Optional[str]
    plan: str
    branding_primary: Optional[str]
    branding_secondary: Optional[str]
    logo_url: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True


class WorkspaceMemberOut(BaseModel):
    id: int
    workspace_id: int
    user_email: str
    role: str
    display_name: Optional[str]
    is_online: bool
    last_seen: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# SERIALIZE HELPERS
# ══════════════════════════════════════════════════

def _dt(v):
    return v.isoformat() if v else None


def _serialize_workspace(w: Workspace) -> dict:
    return {
        "id": w.id,
        "name": w.name,
        "slug": w.slug,
        "owner_email": w.owner_email,
        "plan": w.plan,
        "branding_primary": w.branding_primary,
        "branding_secondary": w.branding_secondary,
        "logo_url": w.logo_url,
        "created_at": _dt(w.created_at),
    }


def _serialize_member(m: WorkspaceMember) -> dict:
    return {
        "id": m.id,
        "workspace_id": m.workspace_id,
        "user_email": m.user_email,
        "role": m.role,
        "display_name": m.display_name,
        "is_online": m.is_online,
        "last_seen": _dt(m.last_seen),
        "created_at": _dt(m.created_at),
    }


def _generate_slug(name: str, db: Session) -> str:
    import re
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = base[:50]
    # vérifie unicité
    existing = db.query(Workspace).filter(Workspace.slug == slug).first()
    if existing:
        slug = f"{base[:45]}-{existing.id + 1}"
    return slug


# ══════════════════════════════════════════════════
# WORKSPACE CRUD
# ══════════════════════════════════════════════════

@router.get("", response_model=List[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db), _: str = Depends(require_auth)):
    """Liste tous les workspaces."""
    ws = db.query(Workspace).order_by(Workspace.created_at.desc()).all()
    return [_serialize_workspace(w) for w in ws]


@router.post("", response_model=WorkspaceOut)
def create_workspace(data: WorkspaceCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    """Crée un workspace. Génère le slug automatiquement si non fourni."""
    slug = data.slug or _generate_slug(data.name, db)
    # vérifie unicité slug
    if db.query(Workspace).filter(Workspace.slug == slug).first():
        raise HTTPException(status_code=409, detail="Slug déjà utilisé")

    w = Workspace(
        name=data.name,
        slug=slug,
        plan=data.plan or "demo",
        branding_primary=data.branding_primary or "#CC9B12",
        branding_secondary=data.branding_secondary or "#0b0b0c",
        logo_url=data.logo_url,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return _serialize_workspace(w)


@router.get("/{workspace_id}", response_model=WorkspaceOut)
def get_workspace(workspace_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    w = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workspace introuvable")
    return _serialize_workspace(w)


@router.put("/{workspace_id}", response_model=WorkspaceOut)
def update_workspace(workspace_id: int, data: WorkspaceUpdate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    w = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workspace introuvable")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(w, k, v)
    db.commit()
    db.refresh(w)
    return _serialize_workspace(w)


@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    w = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workspace introuvable")
    db.delete(w)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════════

@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberOut])
def list_members(workspace_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    w = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workspace introuvable")
    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    return [_serialize_member(m) for m in members]


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberOut)
def add_member(workspace_id: int, data: WorkspaceMemberCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    w = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Workspace introuvable")
    # vérifie doublon email
    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_email == data.user_email,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Membre déjà présent")

    m = WorkspaceMember(
        workspace_id=workspace_id,
        user_email=data.user_email,
        role=data.role or "bd",
        display_name=data.display_name,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _serialize_member(m)


@router.put("/{workspace_id}/members/{member_id}", response_model=WorkspaceMemberOut)
def update_member(workspace_id: int, member_id: int, data: WorkspaceMemberUpdate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    m = db.query(WorkspaceMember).filter(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspace_id == workspace_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return _serialize_member(m)


@router.delete("/{workspace_id}/members/{member_id}")
def remove_member(workspace_id: int, member_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    m = db.query(WorkspaceMember).filter(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspace_id == workspace_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    db.delete(m)
    db.commit()
    return {"ok": True}
