@echo off
echo Shutting down RubyBot Services...
echo --------------------------------------
taskkill /f /im python.exe /t
taskkill /f /im node.exe /t
echo.
echo Ruby is now OFFLINE.
pause
