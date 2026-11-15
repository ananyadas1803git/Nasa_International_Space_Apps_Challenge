"""ASTRA-HEALTH API routes and dataset-backed mission health endpoints."""
from __future__ import annotations
import csv, io, re, json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from . import config, assessment, ml_adapter
from .models import (SessionLocal, ensure_schema, utcnow, User, Mission, Astronaut, HealthRecord, Assessment, Alert, DatasetObservation, MLPrediction)
from .security import db_session, current_user, hash_password, verify_password, issue_token
from . import dataset_store
from .services import (iso, mission_day, history, checkin_info, record_dict, alert_dict, self_assessment_dict,
                       run_and_store_assessment)

ensure_schema()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_schema()
    with SessionLocal() as db:
        # The supplied integrated CSV is the canonical crew/health dataset.
        dataset_store.import_dataset(db)
    if config.SECRET.startswith("CHANGE-THIS"):
        print("[ASTRA-HEALTH] Using the default demo APP_SECRET - fine locally, change it before any deployment.")
    yield


app = FastAPI(title="ASTRA-HEALTH Mission Health API", version="2.0.0", lifespan=lifespan,
              description="Astra-Health mission monitoring API backed by the supplied integrated astronaut dataset. Not a medical device.")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------- schemas
class LoginIn(BaseModel):
    email: str
    password: str


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)


class HealthIn(BaseModel):
    """Software validation bounds only (data quality) - NOT medical decision thresholds."""
    astronaut_id: int
    heart_rate: int = Field(ge=25, le=240)
    systolic_bp: int = Field(ge=60, le=260)
    diastolic_bp: int = Field(ge=30, le=160)
    temperature_c: float = Field(ge=30, le=43)
    glucose_mg_dl: int = Field(ge=20, le=600)
    sleep_hours: float = Field(ge=0, le=24)
    stress_score: Optional[int] = Field(default=None, ge=0, le=10)
    radiation_msv: Optional[float] = Field(default=None, ge=0, le=100)
    source: Literal["manual", "device"] = "manual"
    recorded_at: Optional[datetime] = None

    @model_validator(mode="after")
    def consistency(self):
        if self.systolic_bp <= self.diastolic_bp:
            raise ValueError("Systolic pressure must be higher than diastolic pressure.")
        if self.recorded_at is not None:
            ts = self.recorded_at
            ts = ts.astimezone(timezone.utc).replace(tzinfo=None) if ts.tzinfo else ts
            if ts > utcnow() + timedelta(minutes=5):
                raise ValueError("Timestamp is in the future.")
            if ts < utcnow() - timedelta(days=730):
                raise ValueError("Timestamp is more than two years old.")
            self.recorded_at = ts
        return self




class MLPredictIn(BaseModel):
    crew_code: str = Field(min_length=3, max_length=30)
    features: dict[str, object]

class SelfAssessmentIn(BaseModel):
    astronaut_id: int
    mood: Literal["Very low", "Low", "Steady", "Good", "Very good"]
    fatigue: int = Field(ge=0, le=10)
    symptoms: str = Field(default="None reported", max_length=300)


MOOD_SCORE = {"Very low": 1, "Low": 2, "Steady": 3, "Good": 4, "Very good": 5}


def _astronaut_or_404(db: Session, astronaut_id: int) -> Astronaut:
    a = db.get(Astronaut, astronaut_id)
    if not a:
        raise HTTPException(404, "Astronaut not found.")
    return a


def _auth_payload(user: User) -> dict:
    return {"access_token": issue_token(user.id), "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}


# ---------------------------------------------------------------- public
@app.get("/")
def root():
    return {"service": "astra-health-api", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health(db: Session = Depends(db_session)):
    db.execute(select(1))
    count = db.scalar(select(func.count(DatasetObservation.id))) or 0
    return {"status": "ok", "service": "astra-health-api", "database": "connected", "ml_mode": config.ML_MODE,
            "dataset_loaded": count > 0, "dataset_observations": count}


# ---------------------------------------------------------------- supplied integrated mission dataset
@app.get("/api/dataset/dashboard")
def dataset_dashboard(db: Session = Depends(db_session), user: User = Depends(current_user)):
    return dataset_store.dashboard(db)


@app.get("/api/dataset/catalogue")
def dataset_catalogue(db: Session = Depends(db_session), user: User = Depends(current_user)):
    return dataset_store.catalogue(db)


@app.get("/api/dataset/astronauts/{crew_code}")
def dataset_astronaut(crew_code: str, db: Session = Depends(db_session), user: User = Depends(current_user)):
    result = dataset_store.astronaut_detail(db, crew_code.upper())
    if not result:
        raise HTTPException(404, "Astronaut not found in the integrated dataset.")
    return result


@app.get("/api/dataset/export.csv")
def dataset_export(db: Session = Depends(db_session), user: User = Depends(current_user)):
    out = io.StringIO(newline="")
    with dataset_store.DATASET_PATH.open("r", newline="", encoding="utf-8-sig") as src:
        out.write(src.read())
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=astronaut_health_integrated.csv"})


# ---------------------------------------------------------------- ML inference
@app.get("/api/ml/status")
def ml_status(user: User = Depends(current_user)):
    try:
        from .ml_service import get_engine
        engine = get_engine()
        return {"available": True, "domains": len(engine.models), "models": sum(len(v) for v in engine.models.values()),
                "name": "17-domain champion fold ensemble", "version": "champion-fold-ensemble-v1",
                "mode": "trained", "note": "Research prototype trained on supplied simulated astronaut dataset."}
    except Exception as exc:
        return {"available": False, "error": str(exc), "mode": "unavailable"}

@app.get("/api/ml/template/{crew_code}")
def ml_template(crew_code: str, db: Session = Depends(db_session), user: User = Depends(current_user)):
    detail = dataset_store.astronaut_detail(db, crew_code.upper())
    if not detail:
        raise HTTPException(404, "Astronaut not found in the integrated dataset.")
    try:
        from .ml_service import get_feature_template
        return {"crew_code": crew_code.upper(), "profile": detail["profile"], "features": get_feature_template(detail["latest"])}
    except Exception as exc:
        raise HTTPException(503, f"ML input template unavailable: {exc}")

@app.post("/api/ml/predict", status_code=201)
def ml_predict(data: MLPredictIn, db: Session = Depends(db_session), user: User = Depends(current_user)):
    detail = dataset_store.astronaut_detail(db, data.crew_code.upper())
    if not detail:
        raise HTTPException(404, "Astronaut not found in the integrated dataset.")
    try:
        from .ml_service import predict
        result = predict(data.features, data.crew_code.upper())
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        raise HTTPException(503, f"ML inference failed: {exc}")
    item = MLPrediction(crew_code=data.crew_code.upper(), mission_day=int(result["mission_day"]),
        mission_phase=str(result["mission_phase"]), triage_status=result["triage_status"],
        high_risk_count=result["high_risk_count"], moderate_risk_count=result["moderate_risk_count"],
        input_json=json.dumps(data.features, default=str), result_json=json.dumps(result, default=str))
    db.add(item); db.commit(); db.refresh(item)
    result["prediction_id"] = item.id
    result["created_at"] = iso(item.created_at)
    return result

@app.get("/api/ml/history/{crew_code}")
def ml_history(crew_code: str, db: Session = Depends(db_session), user: User = Depends(current_user)):
    rows = db.query(MLPrediction).filter(MLPrediction.crew_code == crew_code.upper()).order_by(MLPrediction.created_at.desc()).limit(50).all()
    return [{"id": r.id, "crew_code": r.crew_code, "mission_day": r.mission_day, "mission_phase": r.mission_phase,
             "triage_status": r.triage_status, "high_risk_count": r.high_risk_count, "moderate_risk_count": r.moderate_risk_count,
             "created_at": iso(r.created_at), "result": json.loads(r.result_json)} for r in rows]

# ---------------------------------------------------------------- auth
@app.post("/api/auth/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(db_session)):
    email = data.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address.")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, full_name=data.full_name.strip(), password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return _auth_payload(user)


@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(db_session)):
    user = db.scalar(select(User).where(User.email == data.email.strip().lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect.")
    return _auth_payload(user)


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


# ---------------------------------------------------------------- dashboard / crew
def _mission_dict(m: Mission | None) -> dict | None:
    if not m:
        return None
    return {"name": m.name, "code": m.code, "spacecraft": m.spacecraft, "destination": m.destination,
            "environment": m.environment, "phase": m.phase, "status": m.status, "launch_date": m.launch_date,
            "day_number": mission_day(m)}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(db_session), user: User = Depends(current_user)):
    crew, due, since = [], 0, utcnow() - timedelta(hours=24)
    for a in db.scalars(select(Astronaut).order_by(Astronaut.id)).all():
        recs = history(db, a.id, 30)
        latest = recs[-1] if recs else None
        info = checkin_info(recs)
        ev = assessment.evaluate(recs)
        due += info["due_today"]
        crew.append({"id": a.id, "crew_code": a.crew_code, "name": a.full_name, "role": a.role, "nationality": a.nationality,
                     "mission": a.mission.name if a.mission else "Unassigned",
                     "heart_rate": latest.heart_rate if latest else None, "sleep_hours": latest.sleep_hours if latest else None,
                     "stress_score": latest.stress_score if latest else None, "last_record_at": iso(latest.recorded_at) if latest else None,
                     "status": ev["status"], "status_label": ev["status_label"], **info})
    mission = db.scalar(select(Mission).where(Mission.status == "Active"))
    alerts = db.execute(select(Alert, Astronaut.full_name).join(Astronaut, Astronaut.id == Alert.astronaut_id)
                        .order_by(Alert.created_at.desc()).limit(6)).all()
    open_alerts = db.scalar(select(func.count(Alert.id)).where(Alert.status == "Open")) or 0
    last = db.scalar(select(func.max(HealthRecord.recorded_at)))
    return {"mission": _mission_dict(mission), "crew": crew, "alerts": [alert_dict(a, n) for a, n in alerts],
            "metrics": {"crew_count": len(crew), "open_alerts": open_alerts, "checkins_due": due,
                        "records_24h": db.scalar(select(func.count(HealthRecord.id)).where(HealthRecord.recorded_at >= since)) or 0,
                        "mission_day": mission_day(mission)},
            "last_record_at": iso(last), "server_time": iso(utcnow())}


@app.get("/api/astronauts")
def astronauts(db: Session = Depends(db_session), user: User = Depends(current_user)):
    return [{"id": a.id, "crew_code": a.crew_code, "full_name": a.full_name, "role": a.role, "nationality": a.nationality,
             "mission": a.mission.name} for a in db.scalars(select(Astronaut).order_by(Astronaut.id)).all()]


@app.get("/api/astronauts/{astronaut_id}")
def astronaut_detail(astronaut_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    a = _astronaut_or_404(db, astronaut_id)
    recs = history(db, a.id, 60)
    selfs = db.scalars(select(Assessment).where(Assessment.astronaut_id == a.id).order_by(Assessment.recorded_at.desc()).limit(10)).all()
    return {"profile": {"id": a.id, "crew_code": a.crew_code, "full_name": a.full_name, "role": a.role, "nationality": a.nationality,
                        "mission": _mission_dict(a.mission)},
            "records": [record_dict(r) for r in recs[-30:]], "latest": record_dict(recs[-1]) if recs else None,
            "checkin": checkin_info(recs), "assessment": assessment.evaluate(recs),
            "self_assessments": [self_assessment_dict(x) for x in selfs]}


# ---------------------------------------------------------------- health records
@app.get("/api/health-records/{astronaut_id}")
def records(astronaut_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    _astronaut_or_404(db, astronaut_id)
    return [record_dict(r) for r in history(db, astronaut_id, 30)]


@app.post("/api/health-records", status_code=201)
def add_record(data: HealthIn, db: Session = Depends(db_session), user: User = Depends(current_user)):
    _astronaut_or_404(db, data.astronaut_id)
    fields = data.model_dump(exclude={"recorded_at"})
    row = HealthRecord(**fields, recorded_at=data.recorded_at or utcnow(), entered_by=user.full_name)
    db.add(row); db.commit(); db.refresh(row)
    result = run_and_store_assessment(db, data.astronaut_id, row)
    return {"id": row.id, "message": "Health record saved. Values are for prototype monitoring only.", "assessment": result}


@app.get("/api/health-records/{astronaut_id}/export.csv")
def export_csv(astronaut_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    a = _astronaut_or_404(db, astronaut_id)
    out = io.StringIO()
    w = csv.writer(out)
    cols = ["recorded_at_utc", "heart_rate_bpm", "systolic_bp_mmhg", "diastolic_bp_mmhg", "temperature_c", "glucose_mg_dl",
            "sleep_hours", "stress_score_0_10", "radiation_msv", "source", "entered_by"]
    w.writerow(["crew_code"] + cols)
    for r in history(db, astronaut_id, 10_000):
        d = record_dict(r)
        w.writerow([a.crew_code, d["recorded_at"], d["heart_rate"], d["systolic_bp"], d["diastolic_bp"], d["temperature_c"],
                    d["glucose_mg_dl"], d["sleep_hours"], d["stress_score"], d["radiation_msv"], d["source"], d["entered_by"]])
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{a.crew_code}_health_records.csv"'})


# ---------------------------------------------------------------- self-assessments
@app.post("/api/self-assessments", status_code=201)
def add_self_assessment(data: SelfAssessmentIn, db: Session = Depends(db_session), user: User = Depends(current_user)):
    _astronaut_or_404(db, data.astronaut_id)
    row = Assessment(astronaut_id=data.astronaut_id, mood=data.mood, mood_score=MOOD_SCORE[data.mood], fatigue=data.fatigue,
                     symptoms=data.symptoms.strip() or "None reported", entered_by=user.full_name)
    db.add(row); db.commit(); db.refresh(row)
    return {"message": "Self-assessment saved.", "self_assessment": self_assessment_dict(row)}


# ---------------------------------------------------------------- assessment (rule-based + ML boundary)
@app.get("/api/assessment/{astronaut_id}")
def get_assessment(astronaut_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    _astronaut_or_404(db, astronaut_id)
    recs = history(db, astronaut_id, 60)
    latest = recs[-1] if recs else None
    features = {k: getattr(latest, k) for k in ml_adapter.FEATURES} if latest else {}
    return {"rule_based": assessment.evaluate(recs), "ml": ml_adapter.predict(features)}


# ---------------------------------------------------------------- alerts
@app.get("/api/alerts")
def list_alerts(status: Optional[str] = None, db: Session = Depends(db_session), user: User = Depends(current_user)):
    q = select(Alert, Astronaut.full_name).join(Astronaut, Astronaut.id == Alert.astronaut_id).order_by(Alert.created_at.desc()).limit(100)
    if status in ("Open", "Acknowledged"):
        q = q.where(Alert.status == status)
    return [alert_dict(a, n) for a, n in db.execute(q).all()]


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: int, db: Session = Depends(db_session), user: User = Depends(current_user)):
    a = db.get(Alert, alert_id)
    if not a:
        raise HTTPException(404, "Alert not found.")
    a.status = "Acknowledged"
    db.commit()
    return alert_dict(a)
