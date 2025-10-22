@echo off
setlocal
cd /d %~dp0\..

:: Create venv if missing
if not exist venv (
  python -m venv venv || goto :eof
)

:: Activate venv and install deps
call venv\Scripts\activate.bat
if exist requirements.txt (
  pip install -r requirements.txt
)

:: Enable file-based dev persistence; ensure DB persistence is off
set DEV_PERSIST_SELECTION=1
set DB_PERSIST_SELECTION=

:: Start backend (FastAPI)
python -m uvicorn backend.app.main:app --reload --port 8000
