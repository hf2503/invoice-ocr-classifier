@echo off

title 🚀 Lancement de Lux Invoice
echo.
echo __________________________________________

echo 😍 Démarrage de l'application Lux Invoice....

echo __________________________________________
echo .

REM ---------- Vérifie si docker Desktop est en cours d'execution --------

docker info >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo 😬 Docker n'est pas encore prêt. Démarrage de Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo attendre
    timeout /t 20 /nobreak >nul 
)

REM ------------- Demarre le conteneur s'il existe déjà sinon le crée-----------

docker start lux_invoice_app >nul 2>&1