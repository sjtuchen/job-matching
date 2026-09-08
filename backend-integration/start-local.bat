@echo off
set "PY=C:\Users\15485\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0server.py"
pause
