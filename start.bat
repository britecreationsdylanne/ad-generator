@echo off
echo Starting BriteCo Ad Generator...
echo.
SET PATH=C:\Program Files\nodejs;%PATH%
cd /d "%~dp0"
node server.js
pause
