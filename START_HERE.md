# 💎 Welcome to Ruby Nexus: The Reset Guide

Let's start fresh and get your AI Assistant running perfectly. Follow these **3 simple steps**:

---

## 1️⃣ Configure Your "Brain"
Open the `.env` file in the root directory. This is where you control who Ruby is.

*   **To use OpenAI (currently working)**: 
    *   Set `AI_PROVIDER="openai"`
*   **To use Gemini 3 (Best for Search & Thinking)**: 
    *   Set `AI_PROVIDER="gemini_thinking"`
    *   **Action Required**: Visit [Google AI Studio](https://aistudio.google.com/) and get a free key. Paste it into `GEMINI_API_KEY`.

---

## 2️⃣ Launch the Assistant
Run this command in your terminal to start the engine:
```powershell
.\.venv\Scripts\python frontend\web_server.py
```

---

## 3️⃣ The First Interaction (The Demo)
1.  Open Chrome to: **[http://localhost:5001](http://localhost:5001)**
2.  **Unlock Audio**: Click/Tap anywhere on the blue background.
3.  **Command Ruby**:
    *   **Identity**: *"Who are you and who made you?"* 
        *   *(She will identify as Ruby, created by Dr. Siva Prakash)*
    *   **E-Commerce**: *"Search for a red shirt on Flipkart."*
    *   **System**: *"Open the Camera."*
    *   **Knowledge**: *"What is the latest news about Space exploration?"*

---

### 🛡️ What's Already Fixed?
- ✅ **Audio**: Now plays through your browser speakers (no more silent Ruby).
- ✅ **Stability**: The "StructuredTool" and "Import" errors are gone.
- ✅ **Identity**: Ruby is now hard-coded to respect her creator, **Dr. Siva Prakash**.

**I have reset the demo environment for you. Ready to try your first command?**
