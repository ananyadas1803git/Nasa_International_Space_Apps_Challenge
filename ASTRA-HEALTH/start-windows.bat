@echo off
REM One-click launcher for Windows. Double-click this file.
cd /d "%~dp0"
echo === ASTRA-HEALTH: setting up (first run takes a few minutes) ===

set PY=python
where py >nul 2>nul && set PY=py

if not exist backend\.venv\Scripts\python.exe (
  %PY% -m venv backend\.venv
  if errorlevel 1 goto nopython
)
backend\.venv\Scripts\python.exe -m pip install --upgrade pip -q
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
if errorlevel 1 goto pipfail

where npm >nul 2>nul
if errorlevel 1 goto nonode
if not exist frontend\node_modules (
  pushd frontend
  call npm install
  popd
)

start "ASTRA-HEALTH API (port 8000)" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "ASTRA-HEALTH Web (port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"
echo Waiting for servers...
timeout /t 8 >nul
start http://localhost:5173
echo.
echo ASTRA-HEALTH is starting. Login: demo@astravault.test / OrbitReady!2026
echo Close the two black server windows to stop it.
pause
exit /b 0

:nopython
echo ERROR: Python 3.11+ was not found. Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH").
pause
exit /b 1
:pipfail
echo ERROR: Installing Python packages failed. Check your internet connection and try again.
pause
exit /b 1
:nonode
echo ERROR: Node.js was not found. Install the LTS version from https://nodejs.org/ and run this again.
pause
exit /b 1
