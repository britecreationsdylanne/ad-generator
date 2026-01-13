@echo off
echo Starting BriteCo Ad Generator Server...
echo.
cd /d "%~dp0"
python ad_api_server.py
pause
