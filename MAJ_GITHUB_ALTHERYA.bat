@echo off
setlocal EnableExtensions DisableDelayedExpansion
title PUSH APPLI ALTHERYA - GITHUB
cd /d "%~dp0"
echo ==========================================
echo       ENVOI APPLI ALTHERYA SUR GITHUB
echo ==========================================
echo.
echo [1/5] Verification du depot Git...
where git >nul 2>&1
if errorlevel 1 goto :error
if not exist .git goto :dossier
if not exist Dockerfile goto :dossier
if not exist apps\game\package.json goto :dossier
set "DEPOT="
for /f "delims=" %%U in ('git remote get-url origin 2^>nul') do set "DEPOT=%%U"
if /i "%DEPOT%"=="https://github.com/morgandede0-cyber/AppliAltherya.git" goto :depot_ok
if /i "%DEPOT%"=="https://github.com/morgandede0-cyber/AppliAltherya" goto :depot_ok
if /i "%DEPOT%"=="git@github.com:morgandede0-cyber/AppliAltherya.git" goto :depot_ok
echo ERREUR : le depot origin doit etre AppliAltherya.
goto :error
:depot_ok
set "BRANCHE="
for /f "delims=" %%B in ('git symbolic-ref --short HEAD 2^>nul') do set "BRANCHE=%%B"
if not "%BRANCHE%"=="main" (
 echo ERREUR : ce fichier doit etre lance sur la branche main.
 goto :error
)
rem Refuser les donnees sensibles deja suivies : les exclusions ne les retirent pas.
git ls-files | findstr /i /r /c:"\.env" /c:"\.sqlite" /c:"\.db$" /c:"^data/" /c:"^apps/api/data/" /c:"\.pem$" /c:"\.key$" >nul
if not errorlevel 1 (
 echo ERREUR : des fichiers de configuration ou donnees sensibles sont suivis.
 git ls-files | findstr /i /r /c:"\.env" /c:"\.sqlite" /c:"\.db$" /c:"^data/" /c:"^apps/api/data/" /c:"\.pem$" /c:"\.key$"
 echo Faites verifier ces fichiers avant de publier.
 goto :error
)
echo.
echo [2/5] Ajout des fichiers du projet...
git add -A -- . ":(exclude,glob)**/.env*" ":(exclude,glob)**/node_modules/**" ":(exclude,glob)**/dist/**" ":(exclude,top)data/**" ":(exclude,top)apps/api/data/**" ":(exclude,glob)**/__pycache__/**" ":(exclude,glob)**/.venv/**" ":(exclude,glob)**/venv/**" ":(exclude,glob)**/*.sqlite*" ":(exclude,glob)**/*.db" ":(exclude,glob)**/*.log" ":(exclude,glob)**/*.zip" ":(exclude,glob)**/*.pem" ":(exclude,glob)**/*.key"
if errorlevel 1 goto :error
echo.
echo [3/5] Creation du commit...
git diff --cached --quiet
if errorlevel 1 (
 rem Identite technique utilisee pour ce commit seulement.
 git -c user.name="Altherya" -c user.email="altherya@users.noreply.github.com" commit -m "Mise a jour AppliAltherya"
 if errorlevel 1 goto :error
) else (
 echo Aucun changement a commit.
)
echo.
echo [4/5] Recuperation des changements GitHub...
git -c user.name="Altherya" -c user.email="altherya@users.noreply.github.com" pull --rebase origin main
if errorlevel 1 goto :error
echo.
echo [5/5] Envoi sur GitHub...
git push origin main
if errorlevel 1 goto :error
echo.
echo ==========================================
echo      APPLI ALTHERYA ENVOYE AVEC SUCCES
echo ==========================================
echo Verifiez le deploiement dans Coolify.
pause
exit /b 0
:dossier
echo ERREUR : placez ce fichier dans le dossier AppliAltherya clone avec Git.
echo Il doit etre a cote de Dockerfile, apps et du dossier cache .git.
:error
echo.
echo ==========================================
echo UNE ERREUR EST SURVENUE.
echo Lis le message Git affiche juste au-dessus.
echo En cas de conflit pendant le rebase, ne relance pas avant correction.
echo Aucun push force n'est utilise.
echo ==========================================
pause
exit /b 1
