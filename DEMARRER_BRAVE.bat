@echo off
setlocal
cd /d "%~dp0"
where npm >nul 2>&1
if errorlevel 1 (
 echo Node.js est necessaire pour compiler le jeu.
 pause
 exit /b 1
)
pushd apps\game
call npm ci
if errorlevel 1 (
 popd
 pause
 exit /b 1
)
call npm run build
if errorlevel 1 (
 popd
 pause
 exit /b 1
)
popd
py -m pip install -r apps/api/requirements.txt
if errorlevel 1 (
 pause
 exit /b 1
)
if not defined PORT set PORT=8080
echo Ouvrez http://localhost:%PORT% dans Brave une fois le serveur demarre.
py apps/api/server.py
pause
