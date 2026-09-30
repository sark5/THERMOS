@echo off
TITLE THERMOS - Thermal Intelligence Platform (SIH)
echo ======================================================================
echo           THERMOS - OPERATIONAL THERMAL INTELLIGENCE PLATFORM         
echo                       Smart India Hackathon (SIH)                     
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python Virtual Environment...
if not exist ".venv\Scripts\python.exe" (
    echo Error: .venv\Scripts\python.exe not found!
    echo Please make sure the virtual environment exists.
    pause
    exit /b 1
)

echo [2/3] Starting THERMOS AI Engine (FastAPI on http://localhost:8000)...
start "THERMOS AI Engine" cmd /k "cd /d ""%~dp0\aiengine"" && ""%~dp0\.venv\Scripts\uvicorn.exe"" app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Starting THERMOS Command Center Frontend (Vite on http://localhost:5173)...
start "THERMOS Frontend" cmd /k "cd /d ""%~dp0\frontend"" && npm run dev"

echo.
echo All services launched!
echo - AI Engine API: http://localhost:8000 (Swagger docs at /docs)
echo - Frontend Command Center: http://localhost:5173
echo.
timeout /t 3 >nul
start http://localhost:5173
echo Press any key to close this launcher window (services will keep running in background windows).
pause >nul
