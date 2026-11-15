# Architecture

```
Browser (React + Vite, :5173)
   │  /api/*  (Vite dev proxy → no CORS issues)
FastAPI (:8000)  main.py  routes, validation (Pydantic = data quality)
   ├─ security.py       PBKDF2 passwords, HMAC-signed bearer tokens
   ├─ services.py       streaks / reminders / persisting assessments + alerts
   ├─ assessment.py     RULE-BASED layer: compare latest reading with the astronaut's OWN history
   ├─ ml_adapter.py     ML boundary: off | mock | real model (run_model)
   └─ models.py         SQLAlchemy → SQLite (swap DATABASE_URL for PostgreSQL)
```
Follows the blueprint: validation is separate from interpretation (§11.1); no clinical thresholds are invented (§5, §13.5);
every result records its engine/version and every reading its source (§13.6); the website works without the ML model (§11.5).
The assessment sensitivity values in `assessment.py` are placeholders to be replaced by flight-medicine-approved criteria.
