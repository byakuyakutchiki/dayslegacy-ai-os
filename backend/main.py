from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from database import engine, Base, SessionLocal
import models  # noqa: F401 — enregistre les modèles SQLAlchemy
from routers import calls, leads, auth, sophia, audits, workspaces, rooms
from schema_version import ensure_schema

ensure_schema(engine, Base)


def _seed_users():
    """Crée les comptes par défaut si absents (idempotent)."""
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    db = SessionLocal()
    try:
        seeds = [
            {
                "email": os.getenv("ADMIN_EMAIL", "admin@dayslegacy.ai"),
                "password": os.getenv("ADMIN_PASSWORD", "admin"),
                "display_name": "Administrateur",
                "role": "admin",
            },
            {
                "email": os.getenv("GUEST_EMAIL", "invite@dayslegacy.ai"),
                "password": os.getenv("GUEST_PASSWORD", "DL-Guest-2026!"),
                "display_name": "Invité Demo",
                "role": "bd",
            },
        ]
        for s in seeds:
            exists = db.query(models.User).filter(models.User.email == s["email"]).first()
            if not exists:
                db.add(models.User(
                    email=s["email"],
                    password_hash=pwd.hash(s["password"]),
                    role=s["role"],
                    display_name=s["display_name"],
                    is_active=True,
                ))
        db.commit()
    finally:
        db.close()


_seed_users()

app = FastAPI(title="Days Legacy AI OS", version="0.1.0", docs_url="/api/docs")

app.include_router(calls.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(sophia.router, prefix="/api")
app.include_router(audits.router, prefix="/api")
app.include_router(workspaces.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/workspace")
def workspace():
    return FileResponse("static/workspace.html")

@app.get("/")
def root():
    return FileResponse("static/dashboard.html")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
