# API contract — ASTRA-HEALTH dataset build

All `/api/*` routes require `Authorization: Bearer <token>` unless noted. Interactive docs: http://127.0.0.1:8000/docs

| Method & path | Purpose |
|---|---|
| `GET /health` | Service, database connection and integrated dataset import status (public) |
| `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me` | Operator accounts and bearer-token authentication |
| `GET /api/dataset/dashboard` | Mission summary, all dataset astronaut profiles and latest observations |
| `GET /api/dataset/catalogue` | Five hazard domains and seventeen risk domains, with latest crew-level category distributions |
| `GET /api/dataset/astronauts/{crew_code}` | Source profile, latest row and complete chronological observation history for one astronaut |
| `GET /api/dataset/export.csv` | Original integrated CSV export |

## Dataset response semantics

- `crew_code` is the source `astronaut_id` (for example `AST001`).
- `mission_day` and `mission_phase` are read from the source row; no calendar date is inferred.
- `latest` and `history` preserve the complete source payload, including all 147 columns.
- Risk and hazard categories are source-provided labels. The API does not reinterpret them as clinical diagnoses or thresholds.
- The importer is idempotent and loads the bundled canonical CSV on application startup if the observation table is empty.

## Authentication

`POST /api/auth/register` accepts `email`, `password` (10–128 characters) and `full_name`. `POST /api/auth/login` accepts `email` and `password`, returning `{access_token, token_type, user}`.

The local demo account is `demo@astravault.test` / `OrbitReady!2026`. Change or remove it before any deployment.

## Legacy endpoints

Earlier prototype endpoints for manual health records, self-assessments and the previous personal-baseline engine remain in the backend for reference, but the dataset-integrated frontend does not use them. The integrated source rows are read-only in this build to protect their original field definitions and values.
