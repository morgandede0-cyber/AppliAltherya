@echo off
setlocal
cd /d "%~dp0"
if not exist "Dockerfile" (
 echo Placez ce fichier a la racine du projet, a cote du Dockerfile.
 pause
 exit /b 1
)
set errors=0
call :check "apps\game\src\activity.ts" "campaign?:CampaignState"
call :check "apps\game\src\main.ts" "openCampaignMenu"
call :check "apps\game\src\ui\quest-tracker.ts" "s.campaign"
call :check "apps\api\activity.py" "self.campaign=Campaign(self)"
call :check "apps\api\campaign_catalog.json" "S4-Q08"
if not "%errors%"=="0" (
 echo.
 echo Des fichiers sont absents ou anciens. Extraire le ZIP ici en remplacant tous les fichiers.
 pause
 exit /b 1
)
echo.
echo Les fichiers principaux de campagne sont presents.
echo Lancez votre mise a jour GitHub habituelle, puis redeployez dans Coolify.
echo Ce controle local ne confirme pas le contenu de GitHub ou du serveur.
pause
exit /b 0
:check
if not exist "%~1" goto missing
findstr /L /C:"%~2" "%~1" >nul 2>&1
if errorlevel 1 goto missing
echo [OK] %~1
exit /b 0
:missing
set /a errors=errors+1 >nul
echo [A REMPLACER] %~1
exit /b 0
