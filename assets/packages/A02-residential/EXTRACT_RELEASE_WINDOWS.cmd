@echo off
setlocal
cd /d "%~dp0"
where powershell >nul 2>nul
if not errorlevel 1 (
  powershell -NoProfile -File "%~dp0EXTRACT_RELEASE.ps1" -Bundle "%~dp0." -Destination "%~dp0." %*
  if errorlevel 1 goto failed
  goto success
)
echo Built-in PowerShell 5.1 or newer is required for this launcher.
echo Alternative: use installed Python 3.9+ with EXTRACT_RELEASE.py.
goto failed
:success
echo Verified successfully. See the status and output directory printed above.
if "%~1"=="" pause
exit /b 0
:failed
echo Extraction was blocked. Existing different files were not overwritten.
echo Do not bypass your execution policy. See WINDOWS_README_KO.txt for alternatives.
if "%~1"=="" pause
exit /b 1
