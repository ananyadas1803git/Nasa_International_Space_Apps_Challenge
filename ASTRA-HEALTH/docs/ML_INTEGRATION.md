# Astra-Health ML integration

## Runtime design

- The API loads `backend/ml_engine/predict_risk.py` lazily on the first ML request.
- `AstronautRiskTriageEngine` loads the 5 champion cross-validation fold pipelines for each of 17 risk domains (85 model files used at runtime).
- The 255 model artifacts from the handover were reviewed. Only the five-fold champion algorithm selected for each domain by the team's Macro-F1 comparison is bundled; non-champion artifacts are not needed by the runtime inference path.
- `feature_selection.py` is the authoritative input feature map. `integrate_datasets.py` supplies the source-column rename map.
- Domain-specific renamed columns are preferred over generic feature names to avoid collisions between similarly named fields from different source domains.
- Missing model inputs are rejected. They are not silently filled with zero.
- Predictions and the exact submitted feature snapshot are persisted in SQLite (`ml_predictions`).

## User workflow

1. Authenticate using the existing application login.
2. Open **ML prediction** and select an astronaut.
3. The API retrieves that astronaut's latest integrated dataset observation and returns the model input template.
4. The operator can review/edit the 70 visible domain-specific fields and mission context. Some original feature aliases are retained internally to preserve the team's expected model schema.
5. The API validates required features, performs inference across all 17 domains, and stores the input and output.
6. The page renders per-domain LOW/MODERATE/HIGH labels, fold-averaged class scores, P(High), composite GREEN/AMBER/RED status and prediction history.

## API

All endpoints below require the existing Bearer token:

- `GET /api/ml/status` — model availability and runtime counts.
- `GET /api/ml/template/{crew_code}` — latest-record-prefilled model inputs.
- `POST /api/ml/predict` — body: `{ "crew_code": "AST001", "features": { ... } }`.
- `GET /api/ml/history/{crew_code}` — latest 50 saved predictions.

## Model interpretation

The labels are classifications learned from the supplied simulated/research-style dataset. GREEN/AMBER/RED is a composite summary based on the model's LOW/MODERATE/HIGH outputs, not an independently validated clinical triage standard. `confidence`, `prob_low`, `prob_moderate`, and `prob_high` are raw fold-averaged classifier outputs. The supplied code does not establish independent probability calibration. This prototype must not be used for diagnosis, treatment, crew fitness-for-duty or operational flight-safety decisions.

## Runtime dependencies

Use Python 3.11+ and the pinned Scikit-learn 1.8.0 runtime in `backend/requirements.txt`. The model artifacts are Python/Scikit-learn pickle-based files; loading untrusted model artifacts is unsafe. Only use the artifacts bundled with this project or artifacts from a trusted source.
