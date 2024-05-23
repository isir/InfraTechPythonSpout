@echo off
cd /d %~dp0
TITLE Live IR
call venv\\Scripts\\activate.bat
venv\\Scripts\\python.exe main.py
