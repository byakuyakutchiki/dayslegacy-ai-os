from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")


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
