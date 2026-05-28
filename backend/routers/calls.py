"""
Twilio webhooks + WebSocket bridge pour les appels entrants.
"""

from fastapi import APIRouter, WebSocket, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
import asyncio, json, os

from database import get_db
from models import Lead
from services.realtime import run_bridge
from services.scorer import score_lead
from services.notifier import send_sms_bd

router = APIRouter(prefix="/calls", tags=["calls"])

# Stockage temporaire des transcripts en mémoire pendant l'appel
# {call_sid: [{role, content}]}
_active_transcripts: dict = {}


@router.post("/incoming")
async def incoming_call(request: Request):
    """Webhook Twilio : un prospect appelle. On répond avec TwiML pour ouvrir le Media Stream."""
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    _active_transcripts[call_sid] = []

    base_url = os.getenv("BASE_URL", "").rstrip("/")
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{ws_url}/calls/stream/{call_sid}">
      <Parameter name="callSid" value="{call_sid}"/>
    </Stream>
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="text/xml")


@router.websocket("/stream/{call_sid}")
async def media_stream(websocket: WebSocket, call_sid: str, db: Session = Depends(get_db)):
    """WebSocket Twilio Media Streams → bridge OpenAI Realtime."""
    await websocket.accept()
    _active_transcripts.setdefault(call_sid, [])

    # Lance le bridge audio
    await run_bridge(websocket, call_sid, _active_transcripts)

    # Appel terminé — on traite
    transcript = _active_transcripts.pop(call_sid, [])
    if len(transcript) < 2:
        return  # Appel trop court, pas de lead

    # Score et résumé via GPT
    try:
        scored = await score_lead(transcript)
    except Exception:
        scored = {"nom": "Inconnu", "score": 0, "resume": "", "patrimoine_estime": "", "objectif": ""}

    # Récupère le numéro appelant depuis le transcript store metadata
    phone = _active_transcripts.get(f"{call_sid}_phone", "Inconnu")

    # Sauvegarde en base
    lead = Lead(
        call_sid=call_sid,
        phone=phone,
        nom=scored.get("nom", ""),
        prenom=scored.get("prenom", ""),
        patrimoine_estime=scored.get("patrimoine_estime", ""),
        objectif=scored.get("objectif", ""),
        score=scored.get("score", 0),
        transcript=transcript,
        resume=scored.get("resume", ""),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # SMS au BD si score >= 4
    if lead.score >= 4:
        try:
            ok = send_sms_bd(scored, phone)
            if ok:
                lead.sms_envoye = "O"
                db.commit()
        except Exception:
            pass


@router.post("/status")
async def call_status(request: Request):
    """Webhook Twilio status callback — capture le numéro appelant et la durée."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    caller = form.get("From", "Inconnu")
    duration = int(form.get("CallDuration", 0))

    # Stocke le numéro pour que le WebSocket puisse le récupérer
    _active_transcripts[f"{call_sid}_phone"] = caller

    # Met à jour la durée en base si le lead existe
    from database import SessionLocal
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.call_sid == call_sid).first()
        if lead:
            lead.duree_secondes = duration
            db.commit()
    finally:
        db.close()

    return Response(content="OK")
