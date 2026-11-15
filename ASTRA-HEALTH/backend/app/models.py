from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine, inspect, String, Integer, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from .config import DB_URL


def utcnow() -> datetime:
    """Naive UTC datetime (SQLite stores no tz). Replaces the deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(140))
    spacecraft: Mapped[str] = mapped_column(String(100))
    destination: Mapped[str] = mapped_column(String(100))
    environment: Mapped[str] = mapped_column(String(60), default="Space station / LEO")
    phase: Mapped[str] = mapped_column(String(60), default="On-orbit operations")
    status: Mapped[str] = mapped_column(String(30), default="Active")
    launch_date: Mapped[str] = mapped_column(String(20))  # YYYY-MM-DD; mission day is computed from it


class Astronaut(Base):
    __tablename__ = "astronauts"
    id: Mapped[int] = mapped_column(primary_key=True)
    crew_code: Mapped[str] = mapped_column(String(30), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(80))
    nationality: Mapped[str] = mapped_column(String(60))
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))
    mission: Mapped[Mission] = relationship()


class HealthRecord(Base):
    __tablename__ = "health_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    heart_rate: Mapped[int] = mapped_column(Integer)
    systolic_bp: Mapped[int] = mapped_column(Integer)
    diastolic_bp: Mapped[int] = mapped_column(Integer)
    temperature_c: Mapped[float] = mapped_column(Float)
    glucose_mg_dl: Mapped[int] = mapped_column(Integer)
    sleep_hours: Mapped[float] = mapped_column(Float)
    stress_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    radiation_msv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # provenance (blueprint 13.6): who/what supplied the value
    source: Mapped[str] = mapped_column(String(20), default="manual")
    entered_by: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)


class Assessment(Base):
    """Structured self-assessment (mood / fatigue / symptoms)."""
    __tablename__ = "daily_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    mood: Mapped[str] = mapped_column(String(30))
    mood_score: Mapped[int] = mapped_column(Integer, default=3)  # 1 (very low) .. 5 (very good)
    fatigue: Mapped[int] = mapped_column(Integer)  # 0..10
    symptoms: Mapped[str] = mapped_column(String(300), default="None reported")
    entered_by: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)


class Alert(Base):
    __tablename__ = "health_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20))  # Info | Monitor | Review
    category: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(140))
    detail: Mapped[str] = mapped_column(String(400))
    status: Mapped[str] = mapped_column(String(20), default="Open")  # Open | Acknowledged
    source: Mapped[str] = mapped_column(String(40), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AssessmentResult(Base):
    """Stored output of the assessment layer, with the engine/version that produced it (blueprint 13.6)."""
    __tablename__ = "assessment_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"), index=True)
    record_id: Mapped[Optional[int]] = mapped_column(ForeignKey("health_records.id"), nullable=True)
    engine: Mapped[str] = mapped_column(String(60))
    engine_version: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(String(300))
    findings_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def ensure_schema() -> None:
    """Create tables. If an OLD database file with a different schema exists (e.g. from an earlier
    ChatGPT-generated version), move it aside instead of crashing with 'no such column'."""
    if DB_URL.startswith("sqlite"):
        path = DB_URL.replace("sqlite:///", "", 1)
        if os.path.exists(path):
            insp = inspect(engine)
            stale = False
            for table in Base.metadata.sorted_tables:
                if not insp.has_table(table.name):
                    continue
                have = {c["name"] for c in insp.get_columns(table.name)}
                if not {c.name for c in table.columns} <= have:
                    stale = True
                    break
            if stale:
                engine.dispose()
                backup = f"{path}.old-{utcnow().strftime('%Y%m%d-%H%M%S')}"
                os.replace(path, backup)
                print(f"[ASTRA-HEALTH] Old database schema detected - moved to {backup} and created a fresh one.")
    Base.metadata.create_all(engine)


class DatasetObservation(Base):
    """One integrated astronaut/mission-day row from the supplied 147-column dataset."""
    __tablename__ = "dataset_observations"
    __table_args__ = (UniqueConstraint("crew_code", "mission_code", "mission_day", name="uq_dataset_observation"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    crew_code: Mapped[str] = mapped_column(String(30), index=True)
    mission_code: Mapped[str] = mapped_column(String(40), index=True)
    mission_day: Mapped[int] = mapped_column(Integer, index=True)
    mission_phase: Mapped[str] = mapped_column(String(40))
    payload_json: Mapped[str] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class MLPrediction(Base):
    """Persisted output from the bundled 17-domain ML classifier."""
    __tablename__ = "ml_predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    crew_code: Mapped[str] = mapped_column(String(30), index=True)
    mission_day: Mapped[int] = mapped_column(Integer)
    mission_phase: Mapped[str] = mapped_column(String(40))
    triage_status: Mapped[str] = mapped_column(String(20), index=True)
    high_risk_count: Mapped[int] = mapped_column(Integer)
    moderate_risk_count: Mapped[int] = mapped_column(Integer)
    input_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(40), default="champion-fold-ensemble-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
