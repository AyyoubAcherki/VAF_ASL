@echo off
set "VENV_DIR=%~dp0.venv"

echo [1/4] Verification de l'environnement virtuel...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Activation de l'environnement virtuel...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo Avertissement : Aucun environnement virtuel (.venv) n'a ete trouve.
)
echo Appuyez sur une touche pour continuer l'installation...
pause

echo.
echo [2/4] Changement de repertoire vers backend...
cd /D "%~dp0backend"
echo Repertoire actuel : %CD%

echo.
echo [3/4] Installation des dependances...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de l'installation des dependances!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/4] Demarrage de l'application Flask...
echo L'application sera disponible sur: http://127.0.0.1:5000
echo.
python app.py
echo.
echo Le serveur s'est arrete (erreur ou arret normal).
pause
