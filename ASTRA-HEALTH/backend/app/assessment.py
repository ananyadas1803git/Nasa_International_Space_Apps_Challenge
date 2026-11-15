"""Assessment layer (blueprint sections 10.4 and 11).

IMPORTANT - what this engine is and is not
------------------------------------------
* It compares each astronaut's LATEST reading with that SAME astronaut's own recent history
  (personal baseline). It uses plain statistics (z-scores), NOT medical thresholds.
* The blueprint forbids inventing clinical thresholds, diagnoses or treatments. So there are none here.
  The sensitivity parameters below are software placeholders that must be replaced / approved by
  flight-medicine staff before any real use.
* Data-quality validation (units, ranges, timestamps) lives in main.py (Pydantic) and is kept separate
  from health interpretation, as the blueprint requires.
"""
from __future__ import annotations
import statistics
from typing import Sequence

ENGINE = "personal-baseline-statistics"
VERSION = "1.0"
BASELINE_WINDOW = 14      # previous readings used as the personal baseline
MIN_BASELINE = 5          # need at least this many previous readings
Z_ATTENTION = 2.0         # PLACEHOLDER sensitivity (not clinical)
Z_REVIEW = 3.0            # PLACEHOLDER sensitivity (not clinical)

# key -> label, unit, category, minimum SD used so tiny natural variation is not over-flagged
METRICS = {
    "heart_rate":    {"label": "Heart rate",        "unit": "bpm",   "category": "Cardiovascular",     "min_sd": 2.0},
    "systolic_bp":   {"label": "Systolic pressure", "unit": "mmHg",  "category": "Cardiovascular",     "min_sd": 3.0},
    "diastolic_bp":  {"label": "Diastolic pressure","unit": "mmHg",  "category": "Cardiovascular",     "min_sd": 2.5},
    "temperature_c": {"label": "Body temperature",  "unit": "°C",    "category": "Body temperature",   "min_sd": 0.15},
    "glucose_mg_dl": {"label": "Blood glucose",     "unit": "mg/dL", "category": "Metabolic",          "min_sd": 4.0},
    "sleep_hours":   {"label": "Sleep duration",    "unit": "h",     "category": "Sleep & recovery",   "min_sd": 0.4},
    "stress_score":  {"label": "Stress score",      "unit": "/10",   "category": "Behavioral health",  "min_sd": 1.0},
}

STATUS_ORDER = {"insufficient_data": 0, "normal": 1, "attention": 2, "review": 3}
STATUS_LABEL = {
    "insufficient_data": "Not enough history",
    "normal": "Within personal range",
    "attention": "Change from baseline",
    "review": "Marked change - review",
}
NOTE = ("Statistical comparison with this astronaut's own recent readings. Not a diagnosis and not a clinical "
        "threshold. Follow the approved mission medical escalation procedure for any concern.")


def evaluate(records: Sequence) -> dict:
    """records: HealthRecord-like objects sorted oldest -> newest."""
    meta = {"engine": ENGINE, "version": VERSION, "type": "rule-based (statistical, personal baseline)",
            "clinical_thresholds": False, "note": NOTE}
    if len(records) < MIN_BASELINE + 1:
        return {**meta, "status": "insufficient_data", "status_label": STATUS_LABEL["insufficient_data"],
                "summary": f"Need at least {MIN_BASELINE + 1} readings to compare with a personal baseline.",
                "findings": [], "per_metric": {}, "baseline_n": max(len(records) - 1, 0)}

    latest, history = records[-1], list(records[:-1])[-BASELINE_WINDOW:]
    findings, per_metric, worst = [], {}, "normal"
    for key, m in METRICS.items():
        vals = [getattr(r, key) for r in history if getattr(r, key) is not None]
        value = getattr(latest, key)
        if value is None or len(vals) < MIN_BASELINE:
            continue
        mean = statistics.fmean(vals)
        sd = max(statistics.pstdev(vals), m["min_sd"])
        z = (value - mean) / sd
        level = "review" if abs(z) >= Z_REVIEW else "attention" if abs(z) >= Z_ATTENTION else "normal"
        direction = "above" if z > 0 else "below"
        entry = {"metric": key, "label": m["label"], "unit": m["unit"], "category": m["category"],
                 "value": value, "baseline_mean": round(mean, 2), "baseline_sd": round(sd, 2),
                 "z": round(z, 2), "level": level, "direction": direction}
        per_metric[key] = entry
        if level != "normal":
            u = m["unit"] if m["unit"] in ("°C", "/10") else " " + m["unit"]
            entry["message"] = (f"{m['label']} is {abs(value - mean):.1f}{u} {direction} this astronaut's own "
                                f"recent average ({mean:.1f}{u}).")
            findings.append(entry)
            if STATUS_ORDER[level] > STATUS_ORDER[worst]:
                worst = level
    findings.sort(key=lambda f: -abs(f["z"]))
    summary = {"normal": "All indicators are within this astronaut's usual personal range.",
               "attention": f"{len(findings)} indicator(s) differ from this astronaut's personal baseline.",
               "review": f"{len(findings)} indicator(s) differ markedly from this astronaut's personal baseline - flag for medical review."}[worst]
    return {**meta, "status": worst, "status_label": STATUS_LABEL[worst], "summary": summary,
            "findings": findings, "per_metric": per_metric, "baseline_n": len(history)}
