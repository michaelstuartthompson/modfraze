@echo off
REM ------------------------------------------------------------------
REM  ModFraze Trend Scout -- full run with agent + email
REM  Costs money. Mondays and Thursdays only.
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
    echo [%date% %time%] FATAL: venv python not found at %PY%>>"%SCOUT%\logs\scout.log"
    exit /b 1
)
if not exist "%ROOT%\.env" (
    echo [%date% %time%] FATAL: .env missing at %ROOT% -- agent stage cannot run>>"%SCOUT%\logs\scout.log"
    exit /b 1
)

echo.>>"%SCOUT%\logs\scout.log"
echo ===== %date% %time% full run =====>>"%SCOUT%\logs\scout.log"
REM 'x' is listed explicitly because it costs money per post read. It is not in
REM run.py's default sources, so nothing spends unless this line asks it to.
REM Add 'etsy' to this list once your Etsy keystring is approved -- it is free.
"%PY%" run.py --notify --sources google_trends,hackernews,web_news,x >>"%SCOUT%\logs\scout.log" 2>&1
set "RC=%ERRORLEVEL%"
echo ----- exit %RC% ----->>"%SCOUT%\logs\scout.log"
exit /b %RC%
