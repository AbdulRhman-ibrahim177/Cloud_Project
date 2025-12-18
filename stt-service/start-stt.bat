@echo off
REM start-stt.bat - Start STT Service
REM Usage: start-stt.bat

echo.
echo ======================================
echo    STT Service Startup
echo ======================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"
echo [OK] Working directory: %cd%

echo [*] Starting STT Service...
echo [*] Listening on: http://127.0.0.1:8003
echo [*] API Docs: http://127.0.0.1:8003/docs
echo.
echo [!] Press CTRL+C to stop
echo.

python run.py

pause
