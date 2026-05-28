from openai import AsyncOpenAI
import os, json

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCORE_PROMPT = """Tu es un expert en gestion de patrimoine. Analyse cette conversation téléphonique et retourne un JSON.

Conversation :
{transcript}

Retourne UNIQUEMENT ce JSON (sans markdown) :
{{
  "nom": "prénom nom du prospect ou 'Inconnu'",
  "prenom": "",
  "patrimoine_estime": "fourchette ex: <100k / 100k-300k / 300k-1M / >1M ou 'Non précisé'",
  "objectif": "ce que le prospect veut en 1 phrase",
  "resume": "résumé de l'appel en 2-3 phrases, ton professionnel",
  "score": 7.5,
  "score_raison": "pourquoi ce score en 1 phrase"
}}

Critères de score (0-10) :
- 0-3 : curieux, pas de projet concret, patrimoine faible
- 4-6 : projet existe, patrimoine modeste ou non précisé
- 7-8 : projet clair, patrimoine significatif (>200k), prêt à rencontrer un BD
- 9-10 : urgence réelle, patrimoine important (>500k), décisionnaire"""

async def score_lead(transcript: list[dict]) -> dict:
    text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in transcript)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": SCORE_PROMPT.format(transcript=text)}],
        temperature=0,
        max_tokens=400,
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)
