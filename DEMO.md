# 🚀 RubyBot: Free API Demo & Guide

### 💎 The Two Free Replacements
I have already integrated the following "Free Forever" (tier-based) APIs into your project:

1.  **Brain**: **Google Gemini 1.5 Flash**
    *   *Replaces*: OpenAI GPT-4o (which was hitting quota limits).
    *   *Benefit*: High performance, zero cost (within free tier), and much faster for voice commands.
2.  **Voice**: **Microsoft Edge TTS**
    *   *Replaces*: Paid TTS services.
    *   *Benefit*: Professional "Human-like" voices for free.

---

### 🎮 Live Demo Instructions
Since the server is already **RUNNING**, you can see the demo yourself right now:

1.  **Open Chrome**: Go to [http://localhost:5001](http://localhost:5001).
2.  **First Contact**: Click anywhere on the screen (this "wakes up" the browser audio).
3.  **Command Ruby**:
    *   Say: *"Who created you?"* -> Ruby will answer *"MR. DR. SIVA PRAKASH"*.
    *   Say: *"Open YouTube and play trending music"* -> Ruby will instantly open your browser.
    *   Say: *"Search for a laptop on Amazon"* -> Ruby will find it for you.
4.  **Tamil Support**: Ruby also understands and speaks Tamil fluently.

---

### 🛠️ How to Manage Your APIs
Your API configurations are stored in the **`.env`** file. 

| Setting | Value | Description |
| :--- | :--- | :--- |
| `AI_PROVIDER` | `"openai"` / `"gemini"` | Change this to switch your assistant's brain. |
| `GOOGLE_API_KEY` | `your_key_here` | Get a free key at [Google AI Studio](https://aistudio.google.com/). |
| `OPENAI_API_KEY` | `sk-svcacct...` | Use your current key for premium features. |

### 🧩 Files Created for You
- **`.env`**: Central key management.
- **`utiles/api_brain.py`**: The logic that switches between free and paid APIs.
- **`extensions/chrome/`**: Your browser-based remote control for Ruby.

Ruby is now fully optimized for your PC. Open the web link above to start your demo!
