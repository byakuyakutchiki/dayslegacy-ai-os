from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

from database import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

SECRET = os.getenv("JWT_SECRET", "changez-moi")
ALGO = "HS256"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None
    workspace_id: Optional[int] = None
    role: Optional[str] = "bd"


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    display_name: Optional[str]
    workspace_id: Optional[int]
    is_active: bool
    created_at: Optional[str]


def _serialize_user(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "display_name": u.display_name,
        "workspace_id": u.workspace_id,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def _make_token(sub: str, role: str) -> str:
    return jwt.encode(
        {"sub": sub, "role": role, "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET, algorithm=ALGO,
    )


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    admin_pw = os.getenv("ADMIN_PASSWORD", "admin")
    # Admin shortcut: email "admin" checks env var
    if req.email.lower() == "admin":
        if req.password != admin_pw:
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")
        return {"token": _make_token("admin", "admin"), "role": "admin", "display_name": "Admin"}

    # BD user lookup
    user = db.query(User).filter(User.email == req.email, User.is_active == True).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    return {
        "token": _make_token(user.email, user.role),
        "role": user.role,
        "display_name": user.display_name or user.email,
    }


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")


# ══════════════════════════════════════════════════
# USERS CRUD (admin only)
# ══════════════════════════════════════════════════

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [_serialize_user(u) for u in users]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email déjà utilisé")
    u = User(
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        role=data.role or "bd",
        display_name=data.display_name,
        workspace_id=data.workspace_id,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return _serialize_user(u)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserCreate, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if data.display_name is not None:
        u.display_name = data.display_name
    if data.workspace_id is not None:
        u.workspace_id = data.workspace_id
    if data.role:
        u.role = data.role
    if data.password:
        u.password_hash = pwd_context.hash(data.password)
    db.commit()
    db.refresh(u)
    return _serialize_user(u)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(u)
    db.commit()
    return {"ok": True}
