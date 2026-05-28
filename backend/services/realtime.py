"""
Bridge Twilio Media Streams <-> OpenAI Realtime API.
Twilio envoie l'audio G711 µ-law via WebSocket.
On relaie à OpenAI Realtime et on renvoie la réponse audio à Twilio.
"""

import asyncio, json, base64, os
import websockets
from fastapi import WebSocket

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """Tu es Sophia, l'assistante vocale de Days Legacy, un cabinet de gestion de patrimoine.
Ton rôle : accueillir les prospects qui appellent, les mettre à l'aise, et collecter doucement ces informations :
1. Leur prénom et nom
2. Ce qui les amène (projet immobilier, retraite, transmission, placement, autre)
3. Une idée de leur patrimoine financier actuel (fourchette large suffit)
4. S'ils souhaitent être rappelés par un conseiller

Règles absolues :
- Voix chaleureuse, professionnelle, jamais froide
- Jamais de jargon financier complexe
- Si le prospect hésite sur le patrimoine, dis "pas de souci, c'est juste pour vous orienter vers le bon conseiller"
- Maximum 8 minutes d'appel
- Termine toujours par "Un conseiller vous rappellera très prochainement. Bonne journée !"
- Tu représentes Days Legacy, JAMAIS une IA ou un robot si on te demande

Commence par : "Bonjour, vous êtes bien chez Days Legacy. Je suis Sophia, je vais vous orienter. Comment puis-je vous aider aujourd'hui ?"
"""

SESSION_CONFIG = {
    "type": "session.update",
    "session": {
        "turn_detection": {"type": "server_vad"},
        "input_audio_format": "g711_ulaw",
        "output_audio_format": "g711_ulaw",
        "voice": "alloy",
        "instructions": SYSTEM_PROMPT,
        "modalities": ["text", "audio"],
        "temperature": 0.8,
    }
}

async def run_bridge(twilio_ws: WebSocket, call_sid: str, transcript_store: dict):
    """
    Ouvre une connexion OpenAI Realtime et bridge l'audio bidirectionnel.
    transcript_store[call_sid] sera rempli avec les messages au fil de la conversation.
    """
    transcript_store.setdefault(call_sid, [])
    stream_sid = None

    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, additional_headers=headers) as openai_ws:
        await openai_ws.send(json.dumps(SESSION_CONFIG))

        async def twilio_to_openai():
            nonlocal stream_sid
            async for raw in twilio_ws.iter_text():
                msg = json.loads(raw)
                event = msg.get("event")

                if event == "start":
                    stream_sid = msg["start"]["streamSid"]

                elif event == "media":
                    audio = msg["media"]["payload"]
                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": audio,
                    }))

                elif event == "stop":
                    await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                    break

        async def openai_to_twilio():
            async for raw in openai_ws:
                msg = json.loads(raw)
                t = msg.get("type", "")

                if t == "response.audio.delta" and stream_sid:
                    await twilio_ws.send_text(json.dumps({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": msg["delta"]},
                    }))

                elif t == "response.audio_transcript.done":
                    transcript_store[call_sid].append({
                        "role": "assistant",
                        "content": msg.get("transcript", ""),
                    })

                elif t == "conversation.item.input_audio_transcription.completed":
                    transcript_store[call_sid].append({
                        "role": "user",
                        "content": msg.get("transcript", ""),
                    })

        await asyncio.gather(twilio_to_openai(), openai_to_twilio())
