from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from .auth import require_auth

router = APIRouter(prefix="/sophia", tags=["sophia"])
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

SYSTEM_PROMPT = """Tu es Sophia, l'assistante IA patrimoniale de Days Legacy — la première plateforme patrimoniale interactive française.

Tu aides les business developers (BD) à :
- Identifier les prospects prioritaires à contacter aujourd'hui
- Préparer des scripts d'appel personnalisés et convaincants
- Créer des contenus LinkedIn, SEO, emails, scripts vidéo
- Analyser les signaux du marché patrimonial français
- Anticiper les objections et préparer les arguments

Domaines maîtrisés : transmission PME, Pacte Dutreil, succession, donation, SCPI, PER, assurance-vie, SCI familiale, défiscalisation, expatriation fiscale, retraite dirigeant, holding familiale.

Réponds en français. Sois directe, opérationnelle, professionnelle. Ton Days Legacy : premium, humain, expert. Maximum 4 phrases sauf si on demande un script complet."""


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def sophia_chat(req: ChatRequest, _: str = Depends(require_auth)):
    try:
        resp = await _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.message},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return {"response": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
