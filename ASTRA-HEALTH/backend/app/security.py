import hashlib, hmac, base64, json, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import SECRET, TOKEN_HOURS
from .models import SessionLocal, User

_bearer = HTTPBearer(auto_error=False)
ITERATIONS = 240_000


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
        return hmac.compare_digest(candidate, digest)
    except Exception:
        return False


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _sign(msg: str) -> str:
    return _b64(hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).digest())


def issue_token(user_id: int) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    exp = int((datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)).timestamp())
    payload = _b64(json.dumps({"sub": str(user_id), "exp": exp}).encode())
    return f"{header}.{payload}.{_sign(f'{header}.{payload}')}"


def current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer), db: Session = Depends(db_session)) -> User:
    fail = HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")
    if not creds:
        raise fail
    try:
        h, p, s = creds.credentials.split(".")
        if not hmac.compare_digest(s, _sign(f"{h}.{p}")):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(p + "=" * ((4 - len(p) % 4) % 4)))
        if payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("expired")
        user = db.get(User, int(payload["sub"]))
        if not user:
            raise ValueError("user")
        return user
    except Exception:
        raise fail
