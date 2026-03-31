@echo off
cd /d %~dp0

echo Starting Multimodal Video Intelligence on http://127.0.0.1:8000
if not exist .venv\Scripts\python.exe (
    echo.
    echo ERROR: Virtual environment python not found at .venv\Scripts\python.exe
    pause
    exit /b 1
)

.venv\Scripts\python.exe app.py

echo.
echo Server stopped or failed to start.
pause
