# ASTRA-HEALTH — Autonomous Astronaut Health & Risk Monitoring System
### NASA International Space Apps Challenge 2026

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.8.0-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🚀 Overview

**ASTRA-HEALTH** is a dataset-backed, full-stack mission health and predictive risk monitoring platform built for long-duration human spaceflight (such as missions to Mars and Lunar orbital habitats). Developed for the **NASA International Space Apps Challenge 2026**, the system integrates high-dimensional biometric, environmental, and operational telemetry to safeguard astronaut well-being.

The platform grounds its intelligence in NASA’s **5 Human Spaceflight Hazards** and **17 Bio-Medical Risk Domains**, combining an idempotent SQLite-backed longitudinal dataset engine (3,600 telemetry observations across 20 astronauts for 180 mission days with 147 parameters) and an ensemble machine-learning inference pipeline consisting of 85 cross-validation fold models.

> **⚠️ Medical & Operational Disclaimer:**  
> ASTRA-HEALTH is an engineering research prototype designed for telemetry exploration and simulated mission risk monitoring. It is not an FDA-cleared or clinical diagnostic device, does not prescribe medical intervention, and does not establish flight-duty clearance.

---

## 📁 Repository & Folder Structure

```text
NASA_International_Space_Challenge/
├── AstraHealth_Presentation.pptx          # Project presentation slide deck
├── README.md                              # Root repository documentation (this file)
└── ASTRA-HEALTH/                          # Primary application source directory
    ├── DATASET_VALIDATION.txt             # Dataset integrity & key validation verification report
    ├── README.md                          # Inner application guide & setup notes
    ├── TEST_REPORT.md                     # Software verification, syntax & test results
    ├── start.sh                           # One-command startup script (macOS / Linux)
    ├── start-windows.bat                  # One-click startup script (Windows)
    │
    ├── database/                          # Database storage, seed data & provenance
    │   ├── README.md                      # Database documentation & seeding instructions
    │   └── seed/                          # Canonical dataset files & raw archives
    │       ├── ML_DATASET_PROVENANCE.md   # Data lineage, transformation & feature pipeline doc
    │       ├── README.md                  # Seed directory notes
    │       ├── astronaut_health_integrated.csv # Canonical 147-col integrated dataset (3,600 rows)
    │       ├── final_validation_summary.csv    # Validation summary metrics per domain
    │       └── source/                    # Archived raw source data
    │           ├── hazards.zip            # 5 original hazard domain CSVs
    │           └── risks.zip              # 17 original risk domain CSVs
    │
    ├── docs/                              # Technical specifications & design architecture
    │   ├── API_CONTRACT.md                # REST API specifications, payloads & endpoints
    │   ├── ARCHITECTURE.md                # System topology, data flow & boundary separation
    │   ├── DATA_DICTIONARY.md             # 147-feature dictionary, hazards & risk definitions
    │   └── ML_INTEGRATION.md              # 17-domain ML ensemble architecture & runtime specs
    │
    ├── backend/                           # FastAPI backend REST API server
    │   ├── .env.example                   # Environment configuration template
    │   ├── astravault.db                  # Local SQLite database (auto-seeded on first run)
    │   ├── pytest.ini                     # Pytest testing configuration
    │   ├── requirements.txt               # Pinned Python dependencies (FastAPI, Scikit-learn, etc.)
    │   ├── app/                           # Backend application source modules
    │   │   ├── __init__.py
    │   │   ├── assessment.py              # Rule-based longitudinal baseline assessment engine
    │   │   ├── config.py                  # Server configuration, CORS & environment settings
    │   │   ├── dataset_store.py           # Ingestion, JSON-preserving SQLite storage & queries
    │   │   ├── main.py                    # FastAPI application routes & lifecycle management
    │   │   ├── ml_adapter.py              # ML boundary adapter (mock / trained runtime toggle)
    │   │   ├── ml_service.py              # ML inference orchestrator & feature pre-filler
    │   │   ├── models.py                  # SQLAlchemy ORM models (Users, Observations, Predictions)
    │   │   ├── security.py                # PBKDF2 password hashing & HMAC bearer token authentication
    │   │   └── services.py                # Business logic, check-ins, alerts & formatting helpers
    │   ├── tests/                         # Automated unit & integration tests
    │   │   └── test_api.py                # Test suite (Auth, Dataset Import, ML Inference, 17 Domains)
    │   └── ml_engine/                     # Machine Learning training & runtime inference engine
    │       ├── __init__.py
    │       ├── feature_selection.py       # 70-feature mapping, domain grouping & schema validation
    │       ├── fold_level_results.csv     # 5-fold cross-validation performance metrics
    │       ├── integrate_datasets.py      # Dataset integration & column rename pipelines
    │       ├── model_comparison_summary.csv # Macro-F1 model benchmark comparison summary
    │       ├── predict_risk.py            # AstronautRiskTriageEngine runtime inference pipeline
    │       ├── datasets/
    │       │   └── integrated/            # Working directory for dataset generation
    │       └── trained_models/            # 85 champion model artifacts (5 folds x 17 domains)
    │           ├── behavioral_psychiatric/   # Logistic Regression pipelines (5 folds)
    │           ├── bone_changes/             # Logistic Regression pipelines (5 folds)
    │           ├── cardiovascular/           # Random Forest ensembles (5 folds)
    │           ├── decompression_sickness/   # Decision Tree classifiers (5 folds)
    │           ├── dynamic_load_injury/      # Logistic Regression pipelines (5 folds)
    │           ├── food_nutrition/           # Logistic Regression pipelines (5 folds)
    │           ├── host_microorganism/       # Logistic Regression pipelines (5 folds)
    │           ├── hypoxia/                  # Random Forest ensembles (5 folds)
    │           ├── immune_system/            # Random Forest ensembles (5 folds)
    │           ├── physical_fitness/         # Random Forest ensembles (5 folds)
    │           ├── radiation_cancer/         # Decision Tree classifiers (5 folds)
    │           ├── sans/                     # Random Forest ensembles (5 folds)
    │           ├── sensorimotor_vestibular/  # Logistic Regression pipelines (5 folds)
    │           ├── sleep_irregularity/       # Logistic Regression pipelines (5 folds)
    │           ├── spacewalk_injury/         # Random Forest ensembles (5 folds)
    │           ├── systems_operations/       # Logistic Regression pipelines (5 folds)
    │           └── teamwork/                 # Logistic Regression pipelines (5 folds)
    │
    └── frontend/                          # React 18 + Vite frontend single-page application
        ├── .env.example                   # Client-side environment configuration template
        ├── index.html                     # HTML root template with responsive meta tags
        ├── package.json                   # Node.js project manifest & scripts
        ├── package-lock.json              # Deterministic npm package lockfile
        ├── vite.config.js                 # Vite bundler configuration & backend dev proxy
        └── src/                           # Frontend React application source code
            ├── App.jsx                    # Root app layout, hash router & session lifecycle
            ├── api.js                     # Centralized API fetch client with Bearer token injection
            ├── main.jsx                   # React DOM application mount point
            ├── pages.css                  # View-specific styles & responsive grid layouts
            ├── styles.css                 # Global CSS design tokens, typography & spaceflight theme
            ├── components/                # Reusable UI components
            │   ├── Login.jsx              # Operator sign-in & registration modal
            │   └── ui.jsx                 # Badges, metric cards, progress bars & status chips
            ├── data/                      # Educational & domain knowledge bases
            │   └── knowledge.js           # NASA bio-medical knowledge base & organ mapping
            └── pages/                     # Application navigation views
                ├── Assessments.jsx        # Astronaut health check-in & assessment panel
                ├── BodyExplorer.jsx       # Interactive anatomical system telemetry explorer
                ├── CrewHealth.jsx         # Longitudinal physiological trend graphs & vital signs
                ├── Hazards.jsx            # NASA 5 Spaceflight Hazards monitoring & crew distribution
                ├── MLPrediction.jsx       # 17-Domain ML predictive risk triage workbench
                ├── Overview.jsx           # Mission fleet summary, crew roster & high-risk counters
                └── Records.jsx            # Full 147-parameter raw telemetry table & CSV export
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite, Recharts, Lucide Icons | Responsive mission operations UI, interactive charts, and real-time state management |
| **Backend API** | FastAPI, Pydantic v2, Uvicorn, Python 3.11+ | High-performance asynchronous REST API, request schema validation, and auth handling |
| **Database** | SQLite, SQLAlchemy 2.0 ORM | Idempotent startup import, full JSON payload preservation, and indexed telemetry queries |
| **Machine Learning** | Scikit-learn 1.8.0, Joblib, NumPy, Pandas | 85-model ensemble (5-fold cross-validation champion pipelines across 17 risk domains) |
| **Security** | PBKDF2 Password Hashing, HMAC Bearer Tokens | Secure flight surgeon / operator authentication and protected API endpoints |

---

## 📊 Dataset & Medical Risk Framework

ASTRA-HEALTH is pre-loaded with an integrated canonical dataset (`astronaut_health_integrated.csv`) capturing **3,600 mission days** across **20 astronauts** (`AST001`–`AST020`) during a simulated 180-day deep-space exploration mission (`SIM_MISSION_001`) with three distinct flight phases: **Outbound**, **Cruise**, and **Return**.

### NASA 5 Spaceflight Hazards Monitored
1. **Space Radiation:** Solar Particle Events (SPE), Galactic Cosmic Radiation (GCR), and cumulative dosimeter readings (`uGy/day`).
2. **Isolation & Confinement:** Circadian desynchronization, sleep architecture degradation, mood scoring, and psychological stressors.
3. **Distance from Earth:** Autonomous medical protocol enforcement, telemetry latency, and communication blackout handling.
4. **Gravity Fields:** Musculoskeletal deconditioning, bone mineral density loss, cephalad fluid shift, and neuro-vestibular disorientation.
5. **Hostile / Closed Environments:** Cabin atmospheric composition ($CO_2$, $O_2$, pressure), acoustic loads, and environmental microbial tracking.

### 17 Bio-Medical Risk Domains
- Altered Immune System Responses
- Altered Sensorimotor and Vestibular Function
- Cardiovascular Adaptations
- Decompression Sickness
- Dynamic Load Injury
- Host-Microorganism Interactions
- Hypoxia and Altered Atmospheric Pressure
- Inadequate Food and Nutrition
- Inadequate Sleep and Irregular Schedules
- Inadequate Systems Operations Support
- Inadequate Teamwork
- Behavioral Changes and Psychiatric Disorders
- Reduced Cardiorespiratory and Musculoskeletal Fitness
- Spaceflight-Associated Neuro-Ocular Syndrome (SANS)
- Spaceflight-Induced Bone Changes
- Spacewalk (EVA) Injury
- Radiation-Induced Cancers

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python:** Version `3.11+`
- **Node.js:** Version `18+` (LTS recommended)
- **Git**

---

### Option A: Automated One-Command Launch

#### macOS / Linux
```bash
cd ASTRA-HEALTH
chmod +x start.sh
./start.sh
```

#### Windows
Double-click `ASTRA-HEALTH/start-windows.bat` or run in PowerShell:
```powershell
cd ASTRA-HEALTH
.\start-windows.bat
```

The script sets up the Python virtual environment, installs backend and frontend dependencies, starts the FastAPI server on `http://127.0.0.1:8000`, launches the Vite development server on `http://localhost:5173`, and opens the platform in your browser.

---

### Option B: Manual Setup (Two Terminals)

#### Terminal 1 — Backend Server
```bash
cd ASTRA-HEALTH/backend

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Health Status: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Interactive Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Terminal 2 — Frontend Client
```bash
cd ASTRA-HEALTH/frontend

# Install Node dependencies
npm install

# Start Vite dev server (with automatic API proxy)
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🔐 Default Demo Credentials

On startup, the system seeds demo operator credentials for flight medical officers:

- **Email:** `demo@astravault.test`
- **Password:** `OrbitReady!2026`

*New operator accounts can also be registered directly through the application sign-in modal.*

---

## 🧠 Machine Learning Risk Triage Engine

The **ML Prediction Workbench** provides an automated risk triage capability across all 17 risk domains:

1. **Pre-filled Telemetry:** Selecting an astronaut populates 70 model features from their latest mission observation.
2. **What-If Simulation:** Operators can adjust individual parameters (e.g., elevated cabin $CO_2$, reduced sleep, high radiation spike) to evaluate simulated risk shifts.
3. **5-Fold Cross-Validation Ensemble:** Inference executes across 85 champion models (`Random Forest`, `Logistic Regression`, and `Decision Tree` selected via Macro-F1 score evaluation).
4. **Tri-Color Triage:** Generates domain-level predictions (`LOW`, `MODERATE`, `HIGH`) and composite mission triage status (`GREEN`, `AMBER`, `RED`) alongside fold-averaged confidence metrics and $P(\text{High})$ probabilities.
5. **Auditable History:** All submitted inputs and prediction outputs are preserved with timestamps in SQLite (`ml_predictions`).

---

## 🔌 API Summary

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/health` | Service uptime, database connectivity & dataset status | No |
| `POST` | `/api/auth/register` | Register new flight operator account | No |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT bearer token | No |
| `GET` | `/api/auth/me` | Current authenticated operator profile | Yes |
| `GET` | `/api/dataset/dashboard` | Crew status summary, high-risk counts & metrics | Yes |
| `GET` | `/api/dataset/catalogue` | 5 hazards and 17 risks with fleet distributions | Yes |
| `GET` | `/api/dataset/astronauts/{id}` | Full 180-day telemetry timeline for an astronaut | Yes |
| `GET` | `/api/dataset/export.csv` | Export canonical 147-column integrated CSV | Yes |
| `GET` | `/api/ml/status` | ML engine status and loaded model inventory | Yes |
| `GET` | `/api/ml/template/{id}` | Pre-filled 70-feature input template for astronaut | Yes |
| `POST` | `/api/ml/predict` | Execute 17-domain ML risk triage inference | Yes |
| `GET` | `/api/ml/history/{id}` | Historical predictions log for an astronaut | Yes |

---

## 🧪 Testing & Verification

The backend includes automated tests validating data ingestion, API contracts, authorization guards, and ML model inference:

```bash
cd ASTRA-HEALTH/backend
source .venv/bin/activate
pytest -v
```

All 9 test suites verify:
- Automated SQLite schema generation and dataset seeding (3,600 rows).
- 20-crew dashboard calculations and distribution aggregations.
- ML triage pipeline integrity, feature checks, and probability vector bounds ($\sum P = 1.0$).

---

## 📑 Additional Deliverables & Documentation

- **Executive Presentation:** [`AstraHealth_Presentation.pptx`](./AstraHealth_Presentation.pptx) (Located in project root)
- **Data Dictionary:** [`ASTRA-HEALTH/docs/DATA_DICTIONARY.md`](./ASTRA-HEALTH/docs/DATA_DICTIONARY.md)
- **System Architecture:** [`ASTRA-HEALTH/docs/ARCHITECTURE.md`](./ASTRA-HEALTH/docs/ARCHITECTURE.md)
- **ML Integration Guide:** [`ASTRA-HEALTH/docs/ML_INTEGRATION.md`](./ASTRA-HEALTH/docs/ML_INTEGRATION.md)
- **API Contract:** [`ASTRA-HEALTH/docs/API_CONTRACT.md`](./ASTRA-HEALTH/docs/API_CONTRACT.md)

---

## 👥 NASA Space Apps Challenge Team

Created for the **NASA International Space Apps Challenge 2026**.  
*Advancing crew autonomy, digital bio-astronautics, and deep space mission health monitoring.*
