"""Safe adapter around the ML team's 17-domain inference engine."""
from __future__ import annotations
import sys
from pathlib import Path
from functools import lru_cache
from typing import Any
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = BACKEND_DIR / "ml_engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

@lru_cache(maxsize=1)
def get_engine():
    from predict_risk import AstronautRiskTriageEngine
    return AstronautRiskTriageEngine()

def get_feature_config():
    from feature_selection import FEATURE_CONFIG
    return FEATURE_CONFIG

def get_feature_template(source_row: dict[str, Any]) -> dict[str, Any]:
    """Return the 69 model inputs prefilled from the selected astronaut's latest row."""
    engine = get_engine()
    template = {"mission_day": source_row.get("mission_day", 1), "mission_phase": source_row.get("mission_phase", "Cruise")}
    missing = []
    for domain, fold_models in engine.models.items():
        from feature_selection import FEATURE_CONFIG
        for feature in FEATURE_CONFIG[f"{domain}.csv"]:
            mapped = next((ren for ren, orig in engine.domain_reverse_maps.get(domain, {}).items() if orig == feature and ren in source_row), None)
            if mapped:
                # Preserve the exact domain-specific source value as an editable field.
                template[mapped] = source_row[mapped]
            if feature in source_row:
                template[feature] = source_row[feature]
            elif mapped:
                template.setdefault(feature, source_row[mapped])
            else:
                missing.append(f"{domain}.{feature}")
    if missing:
        raise ValueError("The selected dataset row is missing model inputs: " + ", ".join(missing))
    return template

def predict(features: dict[str, Any], crew_code: str) -> dict:
    engine = get_engine()
    required = {"mission_day", "mission_phase"}
    for domain in engine.models:
        from feature_selection import FEATURE_CONFIG
        required.update(FEATURE_CONFIG[f"{domain}.csv"])
    missing = sorted(k for k in required if k not in features or features[k] is None or features[k] == "")
    if missing:
        raise ValueError("Missing required ML inputs: " + ", ".join(missing))
    row = dict(features)
    row["astronaut_id"] = crew_code
    result = engine.predict_single_record(pd.Series(row))
    # Avoid clinical directives: this is a synthetic-data research classifier.
    result["triage_action"] = {"RED": "Multiple/high risk model classifications. Review the underlying data with qualified mission medical personnel.",
                               "AMBER": "One or more moderate risk model classifications. Review trends and source measurements.",
                               "GREEN": "No elevated classes were returned by this model for the submitted inputs."}[result["triage_status"]]
    result["model"] = {"name": "17-domain champion fold ensemble", "version": "champion-fold-ensemble-v1",
                       "status": "research_prototype", "probability_note": "Fold-averaged model scores; not independently calibrated clinical probabilities."}
    result["disclaimer"] = "Experimental predictions from simulated/research-style data. Not a diagnosis, medical advice, or validated flight-safety decision."
    return result
