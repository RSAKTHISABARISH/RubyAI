---
description: Demo command to run the entire RubyBot project
---

# 🚀 RubyBot Demo Command

This workflow automatically cleans up old processes and launches the RubyBot Web UI.

## Step 1: Cleanup
Kill any existing processes on port 5001.

// turbo
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue
```

## Step 2: Environment Check
Ensure the `.env` file contains your actual API keys.

```powershell
# Open .env for editing
notepad .env
```

## Step 3: Launch
Start the web server and open the browser.

// turbo
```powershell
Start-Job -ScriptBlock { & ".\.venv\Scripts\python" "frontend\web_server.py" }
Start-Sleep -Seconds 5
Start-Process "chrome.exe" "http://localhost:5001"
```

---
**Note**: If you see "Invalid API Key" in the console, please ensure you have replaced `your_groq_api_key_here` with your actual key in the `.env` file.
