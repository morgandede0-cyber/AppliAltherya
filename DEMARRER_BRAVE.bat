@echo off
cd /d "%~dp0"
py -m pip install -r apps/api/requirements.txt
if errorlevel 1 (
 pause
 exit /b 1
)
echo Ouvrez http://localhost:8080 dans Brave une fois le serveur demarre.
py apps/api/server.py
pause
