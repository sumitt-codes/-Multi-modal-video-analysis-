@echo off
cd /d %~dp0

echo Starting Multimodal Video Intelligence on http://127.0.0.1:8000
if not exist .venv\Scripts\python.exe (
    echo.
    echo ERROR: Virtual environment python not found at .venv\Scripts\python.exe
    pause
    exit /b 1
)

if "%FFMPEG_BINARY%"=="" (
    for /D %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
        if exist "%%D\ffmpeg-8.1-full_build\bin\ffmpeg.exe" (
            set "FFMPEG_BINARY=%%D\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
        )
    )
)

if not "%FFMPEG_BINARY%"=="" (
    echo Using FFmpeg: %FFMPEG_BINARY%
) else (
    echo WARNING: FFMPEG_BINARY not set. Audio extraction may fail if ffmpeg is not on PATH.
)

.venv\Scripts\python.exe app.py

echo.
echo Server stopped or failed to start.
pause
