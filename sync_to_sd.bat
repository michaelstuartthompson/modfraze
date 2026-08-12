@echo off
REM ============================================================
REM  ModFraze -> SD card mirror
REM
REM  Usage:  sync_to_sd.bat E:
REM          (pass the SD card's drive letter, with the colon)
REM
REM  Desktop is the working copy. The SD card is a MIRROR:
REM  /MIR deletes files on the card that no longer exist here.
REM  Secrets and venvs are excluded on purpose.
REM ============================================================

if "%~1"=="" (
  echo Usage: sync_to_sd.bat DRIVE:   for example  sync_to_sd.bat E:
  exit /b 1
)

set SRC=%~dp0
set DST=%~1\ModFraze

echo Mirroring "%SRC%"  ->  "%DST%"
echo.

robocopy "%SRC%" "%DST%" /MIR /R:2 /W:2 /NFL /NDL /NP ^
  /XD ".venv" "venv" "__pycache__" ".git" "_secrets_DO_NOT_COMMIT" ^
  /XF ".env" "*.env.txt" "twilio_recovery.txt"

REM robocopy exit codes 0-7 are success; 8+ are real failures
if %ERRORLEVEL% GEQ 8 (
  echo.
  echo *** SYNC FAILED (robocopy code %ERRORLEVEL%^) ***
  exit /b %ERRORLEVEL%
)

echo.
echo Sync complete. Secrets were NOT copied to the card by design.
echo If you need to run the agent from the card, create a .env there by hand.
exit /b 0
