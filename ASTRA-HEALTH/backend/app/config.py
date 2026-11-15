"""Settings. Reads backend/.env if present; every value has a safe local default."""
import os
from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))


def _db_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./astravault.db")
    # Resolve relative sqlite paths against backend/ so the DB is always in the same place,
    # no matter which folder uvicorn / pytest was started from.
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and ":memory:" not in url:
        rel = url[len("sqlite:///"):]
        if not os.path.isabs(rel) and not (len(rel) > 1 and rel[1] == ":"):
            url = "sqlite:///" + os.path.normpath(os.path.join(BACKEND_DIR, rel)).replace("\\", "/")
    return url


DB_URL = _db_url()
SECRET = os.getenv("APP_SECRET", "CHANGE-THIS-DEMO-SECRET-BEFORE-DEPLOYMENT")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
ML_MODE = os.getenv("ML_MODE", "trained").lower()
TOKEN_HOURS = 12
