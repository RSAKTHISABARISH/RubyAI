---
description: Complete Workflow for Ruby Voice Assistant (RubyBot)
---

# 🤖 RubyBot Complete Workflow

This workflow guides you through the process of setting up, configuring, and running the Ruby Voice Assistant.

## 1. Prerequisites
- **Python**: Version 3.12 or higher.
- **Microphone & Speakers**: Required for voice interaction.
- **API Keys**:
    - [Groq API Key](https://console.groq.com/keys) (for Whisper STT)
    - [Google AI Studio API Key](https://aistudio.google.com/app/apikey) (for Gemini LLM)

## 2. Setting Up the Environment
Ensure you are in the project root directory and run these commands to prepare your environment.

// turbo
```powershell
# Create a virtual environment
python -m venv .venv

# Upgrade pip and install core dependencies
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install groq edge-tts langchain-groq langchain-google-genai flask flask-socketio eventlet "Flask<3.0"
```

## 3. Configuration
Open the `.env` file in the project root and fill in your API keys:

```text
OPENAI_API_KEY="your_openai_key"  # Optional: for embeddings
GROQ_API_KEY="your_groq_api_key"  # REQUIRED: for Speech-to-Text
GOOGLE_API_KEY="your_google_api_key" # REQUIRED: for Brain/LLM
```

## 4. Running the Website (Modern Interface)
The preferred way to use Ruby is through the Web UI, which includes the pulsing orb and chat history.

// turbo
```powershell
# Start the Web Server
.\.venv\Scripts\python frontend\web_server.py
```

After running, open your browser to:
👉 **[http://localhost:5001](http://localhost:5001)**

## 5. Running the Console Version (Legacy)
If you prefer to run Ruby directly in the terminal without a browser interface:

// turbo
```powershell
# Start the Console version
.\.venv\Scripts\python main.py
```

## 6. Key Features & Tools
Once Ruby is online, you can ask her to perform various tasks:
- **"Play [Video Name] on YouTube"**: Ruby will search and play the video in full screen.
- **"Calculate [Expression]"**: Ruby will solve math problems for you.
- **"Tell me about [Topic]"**: Ruby will use its internal knowledge or search the `docs/` folder if configured.
- **"Switch language to Malayalam/Tamil"**: Ruby supports multilingual switching.

## 7. Troubleshooting
- **Badge shows "Offline"**: Ensure no other process is using port 5001. If it happens, refresh the page.
- **No Sound**: Ensure your speakers are not muted and the volume is up.
- **STT not working**: Check that your `GROQ_API_KEY` is valid and your microphone is set as the default recording device.
