#!/usr/bin/env bash
# One-command launcher for macOS / Linux:  ./start.sh
set -e
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Python 3.11+ is required"; exit 1; }
command -v npm >/dev/null || { echo "Node.js (LTS) is required"; exit 1; }
[ -d backend/.venv ] || python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -q --upgrade pip
backend/.venv/bin/python -m pip install -q -r backend/requirements.txt
[ -d frontend/node_modules ] || (cd frontend && npm install)
trap 'kill 0' EXIT
(cd backend && .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
(cd frontend && npm run dev) &
sleep 5
echo; echo "Open http://localhost:5173   Login: demo@astravault.test / OrbitReady!2026   (Ctrl+C to stop)"
wait
