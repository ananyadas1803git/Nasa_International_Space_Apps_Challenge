"""Import and query the supplied integrated astronaut health dataset.

The CSV is the source of truth. Each row is retained as a JSON payload so that all
147 source fields survive import without lossy remapping into the legacy MVP schema.
"""
from __future__ import annotations
import csv, json, os
from collections import Counter
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .models import DatasetObservation, Mission, Astronaut, User
from .security import hash_password

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATASET_PATH = PROJECT_DIR / "database" / "seed" / "astronaut_health_integrated.csv"
DEMO_EMAIL = "demo@astravault.test"
DEMO_PASSWORD = "OrbitReady!2026"

HAZARDS = [
    {"id":"space_radiation","name":"Space radiation","columns":["radiation_rate_uGy_day","effective_dose_rate_uGy_day","cumulative_dose_uGy","radiation_alert"],"level":"radiation_alert"},
    {"id":"isolation_confinement","name":"Isolation and confinement","columns":["sleep_duration_hours","sleep_quality_score","mood_score","isolation_stress_score","isolation_stress_level"],"level":"isolation_stress_level"},
    {"id":"distance_from_earth","name":"Distance from Earth","columns":["distance_from_earth_km","one_way_communication_delay_seconds","round_trip_communication_delay_seconds","communication_outage","communication_risk_level"],"level":"communication_risk_level"},
    {"id":"gravity_fields","name":"Gravity fields","columns":["gravity_level_g","bone_density_index","gravity_muscle_strength_index","fluid_shift_score","balance_coordination_score","gravity_risk_level"],"level":"gravity_risk_level"},
    {"id":"hostile_environment","name":"Hostile or closed environments","columns":["cabin_co2_ppm","cabin_o2_percent","cabin_pressure_kpa","cabin_temperature_c","cabin_humidity_percent","environmental_stress_score","environmental_alert_level"],"level":"environmental_alert_level"},
]
RISKS = [
    ("Altered immune system responses","immune_risk_level","immune_risk_score","immune_system"),
    ("Altered sensorimotor and vestibular function","sensorimotor_risk_level","sensorimotor_risk_score","sensorimotor_vestibular"),
    ("Cardiovascular adaptations","cardiovascular_risk_level","cardiovascular_risk_score","cardiovascular"),
    ("Decompression sickness","decompression_risk_level","decompression_exposure_score","decompression_sickness"),
    ("Host-microorganism interactions","microorganism_risk_level","microorganism_risk_score","host_microorganism"),
    ("Hypoxia","hypoxia_risk_level","hypoxia_risk_score","hypoxia"),
    ("Inadequate food and nutrition","nutrition_risk_level","nutrition_risk_score","food_nutrition"),
    ("Injury and compromised performance from spacewalks","spacewalk_injury_risk_level","spacewalk_injury_risk_score","spacewalk_injury"),
    ("Reduced cardiorespiratory and musculoskeletal fitness","fitness_risk_level","fitness_risk_score","physical_fitness"),
    ("Spaceflight-associated neuro-ocular syndrome (SANS)","sans_risk_level","sans_risk_score","sans"),
    ("Spaceflight-induced bone changes","bone_change_risk_level","bone_change_risk_score","bone_changes"),
    ("Behavioral changes and psychiatric disorders","behavioral_risk_level","behavioral_risk_score","behavioral_psychiatric"),
    ("Inadequate teamwork","teamwork_risk_level","teamwork_risk_score","teamwork"),
    ("Inadequate sleep and irregular schedules","sleep_risk_level","sleep_risk_score","sleep_irregularity"),
    ("Inadequate systems operations support","systems_support_risk_level","systems_support_risk_score","systems_operations"),
    ("Injury from dynamic loads","dynamic_load_risk_level","dynamic_load_risk_score","dynamic_load_injury"),
    ("Radiation-induced cancers","radiation_cancer_exposure_category","long_term_radiation_exposure_index","radiation_cancer"),
]

def _cast(value: str):
    if value == "": return None
    try:
        n = float(value)
        return int(n) if n.is_integer() and "." not in value and "e" not in value.lower() else n
    except (TypeError, ValueError): return value

def import_dataset(db: Session) -> dict:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Integrated dataset not found: {DATASET_PATH}")
    existing = db.scalar(select(func.count(DatasetObservation.id))) or 0
    if existing:
        return {"status":"already_imported","rows":existing}
    with DATASET_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"astronaut_id","mission_id","mission_day","mission_phase"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Dataset is missing required columns: {sorted(required - set(reader.fieldnames or []))}")
        rows = list(reader)
        if not rows: raise ValueError("Integrated dataset is empty")
        mission_codes = {r["mission_id"] for r in rows}
        if len(mission_codes) != 1:
            raise ValueError(f"Expected one mission in current app scope, found {len(mission_codes)}")
        mission_code = next(iter(mission_codes))
        mission = db.scalar(select(Mission).where(Mission.code == mission_code))
        if not mission:
            mission = Mission(code=mission_code, name="Simulated Mission 001", spacecraft="Not specified in dataset",
                destination="Not specified in dataset", environment="Simulated space mission", phase="Dataset mission phases",
                status="Dataset", launch_date="2026-01-01")
            db.add(mission); db.flush()
        crew_codes = sorted({r["astronaut_id"] for r in rows})
        for code in crew_codes:
            if not db.scalar(select(Astronaut).where(Astronaut.crew_code == code)):
                db.add(Astronaut(crew_code=code, full_name=code, role="Astronaut", nationality="Not specified", mission_id=mission.id))
        if not db.scalar(select(User).where(User.email == DEMO_EMAIL)):
            db.add(User(email=DEMO_EMAIL, full_name="Mission Control Demo", password_hash=hash_password(DEMO_PASSWORD)))
        db.flush()
        batch=[]
        for r in rows:
            payload = {k:_cast(v) for k,v in r.items()}
            batch.append(DatasetObservation(crew_code=r["astronaut_id"], mission_code=r["mission_id"],
                mission_day=int(float(r["mission_day"])), mission_phase=r["mission_phase"],
                payload_json=json.dumps(payload, separators=(",",":"))))
            if len(batch) >= 500:
                db.add_all(batch); db.flush(); batch=[]
        if batch: db.add_all(batch)
        db.commit()
        return {"status":"imported","rows":len(rows),"astronauts":len(crew_codes),"columns":len(reader.fieldnames or [])}

def row_dict(row: DatasetObservation) -> dict:
    return json.loads(row.payload_json)

def latest_rows(db: Session):
    codes = db.scalars(select(Astronaut.crew_code).order_by(Astronaut.crew_code)).all()
    result=[]
    for code in codes:
        row=db.scalar(select(DatasetObservation).where(DatasetObservation.crew_code==code).order_by(DatasetObservation.mission_day.desc()).limit(1))
        if row: result.append(row)
    return result

def dashboard(db: Session) -> dict:
    rows=latest_rows(db)
    all_count=db.scalar(select(func.count(DatasetObservation.id))) or 0
    day_max=db.scalar(select(func.max(DatasetObservation.mission_day))) or 0
    risk_counts=Counter(); hazard_counts=Counter(); crew=[]
    for row in rows:
        d=row_dict(row)
        risk_levels=[d.get(r[1]) for r in RISKS]
        hazard_levels=[d.get(h["level"]) for h in HAZARDS]
        for level in risk_levels:
            if level is not None: risk_counts[str(level)] += 1
        all_levels=risk_levels+hazard_levels
        high=sum(1 for x in all_levels if str(x).lower() in ("high","higher"))
        moderate=sum(1 for x in all_levels if str(x).lower()=="moderate")
        status="High" if high else "Moderate" if moderate else "Low"
        crew.append({"id":row.crew_code,"crew_code":row.crew_code,"name":row.crew_code,"role":"Astronaut",
            "nationality":"Not specified","mission":row.mission_code,"mission_day":row.mission_day,"mission_phase":row.mission_phase,
            "heart_rate":d.get("heart_rate_bpm"),"sleep_hours":d.get("sleep_duration_hours"),"stress_score":d.get("behavioral_stress_score"),
            "status":status,"high_risk_count":high,"moderate_risk_count":moderate,"latest":d})
    for h in HAZARDS:
        for row in rows:
            level=row_dict(row).get(h["level"])
            if level is not None: hazard_counts[h["id"]+":"+str(level)] += 1
    risk_observations=len(rows)*len(RISKS)
    phases=sorted(db.scalars(select(DatasetObservation.mission_phase).distinct()).all())
    high_astronauts=sum(1 for c in crew if c["high_risk_count"] > 0)
    return {"mission":{"name":"Simulated Mission 001","code":rows[0].mission_code if rows else "—","spacecraft":"Not specified in dataset",
            "destination":"Not specified in dataset","environment":"Simulated space mission","phase":"Multiple mission phases","status":"Dataset",
            "launch_date":None,"day_number":day_max},
        "crew":crew,"alerts":[],"metrics":{"crew_count":len(crew),"open_alerts":sum(c["high_risk_count"] for c in crew),
        "checkins_due":0,"records_24h":all_count,"total_observations":all_count,"mission_day":day_max,"high_risk_astronauts":high_astronauts,
        "hazard_count":len(HAZARDS),"risk_count":len(RISKS),"dataset_columns":147,"risk_level_counts":dict(risk_counts),
        "risk_observations":risk_observations},"dataset":{"rows":all_count,"astronauts":len(crew),"mission_days":day_max,
        "mission_phases":phases,"source":"astronaut_health_integrated.csv"}}

def astronaut_detail(db: Session, code: str) -> dict | None:
    rows=db.scalars(select(DatasetObservation).where(DatasetObservation.crew_code==code).order_by(DatasetObservation.mission_day)).all()
    if not rows: return None
    values=[row_dict(r) for r in rows]
    return {"profile":{"crew_code":code,"full_name":code,"role":"Astronaut","nationality":"Not specified",
            "mission":rows[0].mission_code,"observation_count":len(rows)},"latest":values[-1],"history":values}

def catalogue(db: Session) -> dict:
    rows=latest_rows(db)
    hazards=[]
    for h in HAZARDS:
        counts=Counter(str(row_dict(r).get(h["level"]) or "Unknown") for r in rows)
        hazards.append({**h,"level_counts":dict(counts),"crew_count":len(rows)})
    risks=[]
    for name,level_col,score_col,slug in RISKS:
        counts=Counter(str(row_dict(r).get(level_col) or "Unknown") for r in rows)
        scores=[row_dict(r).get(score_col) for r in rows if isinstance(row_dict(r).get(score_col),(int,float))]
        risks.append({"name":name,"slug":slug,"level_field":level_col,"score_field":score_col,"level_counts":dict(counts),
            "mean_score":round(sum(scores)/len(scores),2) if scores else None,"crew_count":len(rows)})
    return {"hazards":hazards,"risks":risks}
