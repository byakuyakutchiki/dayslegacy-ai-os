from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET = os.getenv("JWT_SECRET", "changez-moi")
ALGO = "HS256"

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
def login(req: LoginRequest):
    admin_pw = os.getenv("ADMIN_PASSWORD", "admin")
    if req.password != admin_pw:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    token = jwt.encode(
        {"sub": "admin", "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET, algorithm=ALGO,
    )
    return {"token": token}

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
