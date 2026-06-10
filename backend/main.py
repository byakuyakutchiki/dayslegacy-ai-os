from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from database import engine, Base
import models  # noqa: F401 — enregistre les modèles SQLAlchemy
from routers import calls, leads, auth, sophia

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Days Legacy AI OS", version="0.1.0", docs_url="/api/docs")

app.include_router(calls.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(sophia.router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/")
def root():
    return FileResponse("static/dashboard.html")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
