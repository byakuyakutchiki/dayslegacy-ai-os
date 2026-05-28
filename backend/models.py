from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
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
