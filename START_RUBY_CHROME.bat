@echo off
echo 🚀 Starting RubyBot Voice Assistant...
echo.
echo ⚠️ PLEASE ENSURE YOUR .env FILE IS UPDATED WITH VALID API KEYS!
echo.

:: Kill any existing process on port 5001
powershell -Command "Stop-Process -Id (Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue"

:: Start the Python backend in a new window
echo 📡 Starting Web Server...
start "RubyBot Server" cmd /k "python frontend/web_server.py"

:: Wait for server to initialize
echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak > nul

:: Open Chrome
echo 🌐 Opening Chrome...
start chrome "http://localhost:5001"

echo.
echo ✅ RubyBot is running! 
echo Keep the [RubyBot Server] window open while using the assistant.
pause
