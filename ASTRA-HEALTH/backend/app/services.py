from __future__ import annotations
import json
from datetime import datetime, timedelta, date
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import assessment
from .models import Astronaut, HealthRecord, Assessment, Alert, AssessmentResult, Mission, utcnow

SEVERITY = {"attention": "Monitor", "review": "Review"}


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat(timespec="seconds") + "Z" if dt else None


def mission_day(m: Mission | None) -> int:
    if not m:
        return 0
    try:
        return max((utcnow().date() - date.fromisoformat(m.launch_date)).days + 1, 1)
    except ValueError:
        return 1


def history(db: Session, astronaut_id: int, limit: int = 60) -> list[HealthRecord]:
    """Newest `limit` records, returned oldest -> newest."""
    rows = db.scalars(select(HealthRecord).where(HealthRecord.astronaut_id == astronaut_id)
                      .order_by(HealthRecord.recorded_at.desc()).limit(limit)).all()
    return list(reversed(rows))


def checkin_info(records: list[HealthRecord]) -> dict:
    """Reminder + streak, derived from the records (UTC calendar days)."""
    days = {r.recorded_at.date() for r in records}
    today = utcnow().date()
    due = today not in days
    cursor = today if not due else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return {"due_today": due, "streak_days": streak}


def record_dict(r: HealthRecord) -> dict:
    return {"id": r.id, "recorded_at": iso(r.recorded_at), "heart_rate": r.heart_rate, "systolic_bp": r.systolic_bp,
            "diastolic_bp": r.diastolic_bp, "temperature_c": r.temperature_c, "glucose_mg_dl": r.glucose_mg_dl,
            "sleep_hours": r.sleep_hours, "stress_score": r.stress_score, "radiation_msv": r.radiation_msv,
            "source": r.source, "entered_by": r.entered_by}


def alert_dict(a: Alert, name: str | None = None) -> dict:
    return {"id": a.id, "astronaut_id": a.astronaut_id, "astronaut_name": name, "severity": a.severity,
            "category": a.category, "title": a.title, "detail": a.detail, "status": a.status,
            "source": a.source, "created_at": iso(a.created_at)}


def self_assessment_dict(x: Assessment) -> dict:
    return {"id": x.id, "recorded_at": iso(x.recorded_at), "mood": x.mood, "mood_score": x.mood_score,
            "fatigue": x.fatigue, "symptoms": x.symptoms, "entered_by": x.entered_by}


def run_and_store_assessment(db: Session, astronaut_id: int, record: HealthRecord | None = None) -> dict:
    """Evaluate, persist the result (with engine + version) and raise de-duplicated alerts."""
    result = assessment.evaluate(history(db, astronaut_id))
    db.add(AssessmentResult(astronaut_id=astronaut_id, record_id=record.id if record else None,
                            engine=result["engine"], engine_version=result["version"], status=result["status"],
                            summary=result["summary"][:300], findings_json=json.dumps(result["findings"])))
    for f in result["findings"]:
        title = f"{f['label']} differs from personal baseline"
        exists = db.scalar(select(Alert.id).where(Alert.astronaut_id == astronaut_id, Alert.title == title, Alert.status == "Open"))
        if not exists:
            db.add(Alert(astronaut_id=astronaut_id, severity=SEVERITY[f["level"]], category=f["category"], title=title,
                         detail=(f["message"] + " Statistical flag only - confirm per approved mission procedure.")[:400],
                         source="assessment-engine"))
    db.commit()
    return result
