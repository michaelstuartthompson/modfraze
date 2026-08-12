@echo off
REM ------------------------------------------------------------------
REM  ModFraze Trend Scout -- daily collect (free stage, no API calls)
REM  Builds the velocity baseline. Run every day.
REM
REM  Paths updated 2026-08-12 for the consolidated ModFraze folder.
REM  The venv and .env live at the ModFraze ROOT; run.py lives in the
REM  scout folder, so those are two different directories now.
REM ------------------------------------------------------------------
setlocal
set "ROOT=C:\Users\miket\Desktop\ModFraze"
set "SCOUT=%ROOT%\agents\trend_scout"
set "PY=%ROOT%\.venv\Scripts\python.exe"

cd /d "%SCOUT%" || exit /b 1
if not exist "%SCOUT%\logs" mkdir "%SCOUT%\logs"
if not exist "%PY%" (
    echo [%date% %time%] FATAL: venv python not found at %PY%>>"%SCOUT%\logs\collect.log"
    exit /b 1
)

echo.>>"%SCOUT%\logs\collect.log"
echo ===== %date% %time% collect-only =====>>"%SCOUT%\logs\collect.log"
"%PY%" run.py --collect-only --quiet >>"%SCOUT%\logs\collect.log" 2>&1
set "RC=%ERRORLEVEL%"
echo ----- exit %RC% ----->>"%SCOUT%\logs\collect.log"
exit /b %RC%
