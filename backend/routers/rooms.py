from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Room, Message, Meeting, Workspace
from routers.auth import require_auth

router = APIRouter(prefix="/rooms", tags=["rooms"])


# ══════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════

class RoomCreate(BaseModel):
    workspace_id: int
    name: str
    type: Optional[str] = "meeting"
    status: Optional[str] = "active"
    created_by: Optional[str] = None


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class MessageCreate(BaseModel):
    sender_email: str
    sender_name: Optional[str] = None
    content: str
    type: Optional[str] = "text"


class MessageOut(BaseModel):
    id: int
    room_id: int
    sender_email: str
    sender_name: Optional[str]
    content: str
    type: str
    created_at: Optional[str]

    class Config:
        from_attributes = True


class MeetingOut(BaseModel):
    id: int
    room_id: int
    title: Optional[str]
    scheduled_at: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    status: str
    screen_share_url: Optional[str]
    recording_url: Optional[str]
    created_by: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True


class RoomOut(BaseModel):
    id: int
    workspace_id: int
    name: str
    type: str
    status: str
    created_by: Optional[str]
    created_at: Optional[str]
    messages: List[MessageOut] = []
    meetings: List[MeetingOut] = []

    class Config:
        from_attributes = True


class RoomListOut(BaseModel):
    id: int
    workspace_id: int
    name: str
    type: str
    status: str
    created_by: Optional[str]
    created_at: Optional[str]
    message_count: int = 0

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# SERIALIZE HELPERS
# ══════════════════════════════════════════════════

def _dt(v):
    return v.isoformat() if v else None


def _serialize_message(m: Message) -> dict:
    return {
        "id": m.id,
        "room_id": m.room_id,
        "sender_email": m.sender_email,
        "sender_name": m.sender_name,
        "content": m.content,
        "type": m.type,
        "created_at": _dt(m.created_at),
    }


def _serialize_meeting(m: Meeting) -> dict:
    return {
        "id": m.id,
        "room_id": m.room_id,
        "title": m.title,
        "scheduled_at": _dt(m.scheduled_at),
        "started_at": _dt(m.started_at),
        "ended_at": _dt(m.ended_at),
        "status": m.status,
        "screen_share_url": m.screen_share_url,
        "recording_url": m.recording_url,
        "created_by": m.created_by,
        "created_at": _dt(m.created_at),
    }


def _serialize_room_list(r: Room) -> dict:
    return {
        "id": r.id,
        "workspace_id": r.workspace_id,
        "name": r.name,
        "type": r.type,
        "status": r.status,
        "created_by": r.created_by,
        "created_at": _dt(r.created_at),
        "message_count": len(r.messages) if r.messages else 0,
    }


def _serialize_room_detail(r: Room) -> dict:
    return {
        "id": r.id,
        "workspace_id": r.workspace_id,
        "name": r.name,
        "type": r.type,
        "status": r.status,
        "created_by": r.created_by,
        "created_at": _dt(r.created_at),
        "messages": [_serialize_message(m) for m in (r.messages or [])],
        "meetings": [_serialize_meeting(m) for m in (r.meetings or [])],
    }


# ══════════════════════════════════════════════════
# ROOM CRUD
# ══════════════════════════════════════════════════

@router.get("", response_model=List[RoomListOut])
def list_rooms(
    workspace_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Liste les rooms. Filtrable par workspace_id."""
    q = db.query(Room)
    if workspace_id:
        q = q.filter(Room.workspace_id == workspace_id)
    rooms = q.order_by(Room.created_at.desc()).all()
    return [_serialize_room_list(r) for r in rooms]


@router.post("", response_model=RoomOut)
def create_room(data: RoomCreate, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    """Crée une room dans un workspace."""
    ws = db.query(Workspace).filter(Workspace.id == data.workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace introuvable")

    r = Room(
        workspace_id=data.workspace_id,
        name=data.name,
        type=data.type or "meeting",
        status=data.status or "active",
        created_by=data.created_by,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _serialize_room_detail(r)


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    """Détail d'une room avec messages et meetings."""
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")
    return _serialize_room_detail(r)


@router.put("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: int,
    data: RoomUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return _serialize_room_detail(r)


@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db), _: str = Depends(require_auth)):
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════════════

@router.get("/{room_id}/messages", response_model=List[MessageOut])
def list_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 50,
    since: Optional[str] = Query(None, description="ISO datetime — ne retourne que les messages créés après ce timestamp"),
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Liste les messages d'une room (pagination + filtre since pour polling)."""
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")
    q = db.query(Message).filter(Message.room_id == room_id)
    if since:
        from datetime import datetime
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            q = q.filter(Message.created_at > since_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Paramètre 'since' invalide (format ISO 8601 attendu)")
    msgs = q.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    return [_serialize_message(m) for m in msgs]


@router.post("/{room_id}/messages", response_model=MessageOut)
def post_message(
    room_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Poste un message dans une room."""
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")

    m = Message(
        room_id=room_id,
        sender_email=data.sender_email,
        sender_name=data.sender_name,
        content=data.content,
        type=data.type or "text",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _serialize_message(m)


# ══════════════════════════════════════════════════
# MEETINGS (placeholder visuel — pas de visio réelle)
# ══════════════════════════════════════════════════

@router.get("/{room_id}/meetings", response_model=List[MeetingOut])
def list_meetings(
    room_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Liste les meetings d'une room."""
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")
    meets = db.query(Meeting).filter(Meeting.room_id == room_id).order_by(Meeting.created_at.desc()).all()
    return [_serialize_meeting(m) for m in meets]


@router.post("/{room_id}/meetings", response_model=MeetingOut)
def create_meeting(
    room_id: int,
    title: Optional[str] = None,
    scheduled_at: Optional[datetime] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    """Crée un meeting (placeholder) dans une room."""
    r = db.query(Room).filter(Room.id == room_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Room introuvable")

    m = Meeting(
        room_id=room_id,
        title=title or f"Réunion {r.name}",
        scheduled_at=scheduled_at,
        status="scheduled",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _serialize_meeting(m)
