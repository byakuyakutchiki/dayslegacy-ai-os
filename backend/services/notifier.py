from twilio.rest import Client
import os

def send_sms_bd(lead_data: dict, phone_lead: str) -> bool:
    """Envoie un SMS récap au BD après chaque appel qualifié."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    bd_number = os.getenv("BD_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number, bd_number]):
        return False

    score = lead_data.get("score", 0)
    nom = lead_data.get("nom", "Inconnu")
    patrimoine = lead_data.get("patrimoine_estime", "Non précisé")
    objectif = lead_data.get("objectif", "")
    resume = lead_data.get("resume", "")

    # Indicateur visuel du score
    if score >= 8:
        flag = "🔥"
    elif score >= 6:
        flag = "⭐"
    else:
        flag = "📞"

    body = (
        f"{flag} NOUVEAU PROSPECT — Score {score}/10\n"
        f"Nom : {nom}\n"
        f"Tél : {phone_lead}\n"
        f"Patrimoine : {patrimoine}\n"
        f"Objectif : {objectif}\n\n"
        f"{resume}\n\n"
        f"→ Tableau de bord : {os.getenv('BASE_URL', '')}/dashboard"
    )

    client = Client(account_sid, auth_token)
    client.messages.create(body=body, from_=from_number, to=bd_number)
    return True
