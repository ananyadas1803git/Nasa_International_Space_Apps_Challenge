# ASTRA-HEALTH — Astronaut Health Monitoring System

Dataset-backed full-stack application for the NASA Space Apps Challenge 2026. The supplied integrated astronaut-health dataset is the application's source of truth.

**Frontend:** React 18 + Vite + Recharts  
**Backend:** FastAPI + SQLAlchemy 2 + SQLite  
**Dataset:** 3,600 observations · 20 astronaut IDs · 180 mission days each · 147 columns · 1 mission · 3 mission phases  
**Framework:** 5 human-spaceflight hazards and 17 health-risk domains

> **Important:** The supplied data contains simulated/research-style values and source-provided category labels. This application is a prototype for monitoring and exploration, not a medical device. It does not diagnose, prescribe, or establish clinical thresholds. Follow approved mission medical procedures.

## Quick start — Windows

Prerequisites: Python 3.11+ and Node.js 18+.

1. Extract the ZIP.
2. Double-click `start-windows.bat`.
3. Wait for both terminals to start, then open `http://localhost:5173`.
4. Sign in using the demo credentials below, or create an operator account.

**Demo login**
- Email: `demo@astravault.test`
- Password: `OrbitReady!2026`

The backend imports `database/seed/astronaut_health_integrated.csv` into SQLite automatically on first startup. It creates the 20 dataset astronaut profiles and imports all 3,600 complete observation rows. The import is idempotent; later starts do not duplicate the rows.

## Manual start — two terminals

**Terminal 1 — backend (PowerShell):**
```powershell
cd backend
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend:**
```powershell
cd frontend
npm install
npm run dev
```

Check backend health at `http://127.0.0.1:8000/health` and API docs at `http://127.0.0.1:8000/docs`.

## Application modules

- **Overview:** all 20 astronauts, latest observations, mission-day span, risk category distribution and hazard framework.
- **Crew health:** select any astronaut, explore longitudinal trends across key fields, inspect the latest labels across all 17 risk domains and review recent observations.
- **Health records:** inspect the complete latest source row, review recent mission-day records and export the original integrated CSV. The imported source dataset is read-only in this build to preserve its provenance.
- **Body explorer:** educational body-region navigation linked to actual dataset measurements.
- **Hazard watch:** all five hazards and seventeen risk domains with source-field names and latest crew-level category distributions.
- **Risk assessment:** selected astronaut's latest source-provided hazard/risk labels and representative underlying measurements. No invented ML prediction or clinical rule engine is shown as active.

## Dataset files included

- `database/seed/astronaut_health_integrated.csv` — canonical 147-column source used by the application importer.
- `database/seed/source/hazards.zip` — original five hazard-domain CSVs supplied separately.
- `database/seed/source/risks.zip` — original seventeen risk-domain CSVs supplied separately.

The integrated dataset contains one mission ID (`SIM_MISSION_001`), astronaut IDs `AST001`–`AST020`, mission days 1–180, and phases Outbound, Cruise and Return. Names, nationalities and roles are not present in the dataset; the application therefore uses astronaut IDs and does not fabricate personal details.

## Data/API design

Every imported source row is stored intact as JSON in `dataset_observations`, indexed by astronaut ID, mission ID and mission day. This avoids lossy mapping: all original columns remain available through the API. The legacy manual-entry MVP tables remain in the codebase for future development but are not used to populate or reinterpret the supplied integrated dataset.

Authenticated dataset endpoints:
- `GET /api/dataset/dashboard`
- `GET /api/dataset/catalogue`
- `GET /api/dataset/astronauts/{crew_code}`
- `GET /api/dataset/export.csv`

## Tests

From `backend/`:
```powershell
.venv\Scripts\python.exe -m pytest -q
```
The test suite checks dataset import, 20-astronaut dashboard counts, all five hazards and seventeen risks, 180-day detail history, authentication, unknown astronaut handling and CSV export.

## Reset / re-import

Stop the backend and delete `backend/astravault.db`. Start the backend again; it recreates the schema and imports the bundled CSV. Keep the source CSV in its included path.

## Security / deployment notes

This package is configured for local demonstration. Before deployment, set a strong unique `APP_SECRET`, use a production database, restrict CORS, enforce role-based authorization, protect exports, add audit logging/rate limiting, and review data governance. The demo operator password is public in this README and must not be reused in a deployed environment.

## ML prediction module (integrated)

The **ML prediction** workspace uses the ML team's bundled Scikit-learn champion fold ensemble. It loads 5 cross-validation fold pipelines for each of 17 risk domains (255 `.joblib` artifacts total). On first access the backend loads the models into memory; subsequent predictions reuse the loaded engine.

1. Select an astronaut.
2. The form pre-fills the 69 model features and mission context from that astronaut's latest integrated observation.
3. Review/edit the values and submit.
4. The API runs the 17-domain model ensemble and stores the input snapshot and output in `ml_predictions`.
5. Prediction history is available for that astronaut.

Authenticated ML endpoints: `GET /api/ml/status`, `GET /api/ml/template/{crew_code}`, `POST /api/ml/predict`, `GET /api/ml/history/{crew_code}`.

**Interpretation and limitations:** The supplied model artifacts were trained on simulated/research-style astronaut data with only 20 astronaut groups. The returned LOW/MODERATE/HIGH labels and GREEN/AMBER/RED composite are experimental model classifications, not diagnoses, clinical risk estimates, calibrated medical probabilities, or flight-safety decisions. The displayed class score and P(High) are raw fold-averaged classifier probabilities; the team's code does not establish independent probability calibration. The UI deliberately replaces the source CLI's prescriptive medical directives with cautious review language. Validate model provenance, feature definitions, calibration, class balance and generalization with qualified domain experts before any operational use.

### Bundled ML assets

`backend/ml_engine/` contains the ML team's prediction code, feature configuration, dataset integration mapping, champion model artifacts and model comparison reports. Training datasets and exploratory/legacy scripts are not required at runtime and are not duplicated into this application package. The original integrated CSV remains under `database/seed/` and is the source used to prefill new prediction inputs.
