@echo off
cd /d %~dp0
echo Activating Virtual Environment...
call venv\Scripts\activate

:loop
echo Starting Waitress...
start /B python -m waitress --host 127.0.0.1 --port=5000 app:app

echo Watching for file changes...
watchmedo shell-command --patterns="*.py" --recursive --command="taskkill /F /IM python.exe & python -m waitress --host 127.0.0.1 --port=5000 app:app" .
timeout /t 2
goto loop
