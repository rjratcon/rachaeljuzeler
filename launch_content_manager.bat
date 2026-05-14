@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3.13 rachael_content_manager.py
    if %errorlevel%==0 goto end
    py rachael_content_manager.py
    if %errorlevel%==0 goto end
)

python rachael_content_manager.py

:end
