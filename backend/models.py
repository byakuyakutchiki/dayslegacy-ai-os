from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(64), unique=True, index=True)     # ID Twilio de l'appel
    phone = Column(String(20))                                  # Numéro appelant
    nom = Column(String(100))
    prenom = Column(String(100))
    patrimoine_estime = Column(String(50))                      # ex: "200k-500k"
    objectif = Column(Text)                                     # Ce que le prospect veut
    score = Column(Float, default=0)                            # 0.0 à 10.0
    transcript = Column(JSON, default=list)                     # [{role, content}]
    resume = Column(Text)                                       # Résumé GPT
    sms_envoye = Column(String(1), default="N")                # O/N
    duree_secondes = Column(Integer, default=0)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditClient(Base):
    __tablename__ = "audit_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), nullable=False)
    sector = Column(String(100))
    contact_name = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    ca_estime = Column(String(50))
    effectif = Column(Integer)
    patrimoine_dirigeant = Column(String(50))
    statut = Column(String(20), default="en_cours")  # en_cours, valide, archive
    score_audit = Column(Float, default=0)  # 0.0 à 10.0
    resume_global = Column(Text)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, index=True)
    owner_email = Column(String(100))
    plan = Column(String(20), default="demo")
    branding_primary = Column(String(7), default="#CC9B12")
    branding_secondary = Column(String(7), default="#0b0b0c")
    logo_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="workspace", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_email = Column(String(100), nullable=False)
    role = Column(String(20), default="bd")
    display_name = Column(String(100))
    avatar_url = Column(String(255))
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="members")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="meeting")
    status = Column(String(20), default="active")
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="room", cascade="all, delete-orphan")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    title = Column(String(200))
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    screen_share_url = Column(String(255))
    recording_url = Column(String(255))
    status = Column(String(20), default="scheduled")
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="meetings")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    name = Column(String(200), nullable=False)
    file_url = Column(String(255))
    mime_type = Column(String(100))
    size_bytes = Column(Integer)
    uploaded_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="documents")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    sender_email = Column(String(100), nullable=False)
    sender_name = Column(String(100))
    content = Column(Text, nullable=False)
    type = Column(String(20), default="text")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="messages")


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_clients.id"), nullable=False)
    category = Column(String(50))  # fiscal, social, juridique, patrimonial, strategique
    severity = Column(String(20))  # critique, eleve, moyen, faible
    title = Column(String(200), nullable=False)
    description = Column(Text)
    recommendation = Column(Text)
    potential_gain = Column(String(50))
    status = Column(String(20), default="ouvert")  # ouvert, en_cours, resolu
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    audit = relationship("AuditClient", back_populates="findings")
