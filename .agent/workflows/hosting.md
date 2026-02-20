---
description: How to host RubyBot for remote access
---

# 🌐 Hosting RubyBot

Since RubyBot needs access to your **Microphone, Speakers, and PC Applications**, it is best to run it on your local machine. However, if you want to access your Ruby Dashboard from your phone or another computer, follow these steps.

## Method 1: Using Ngrok (Recommended)
This is the best way because it keeps Ruby running on your PC (so she can still hear and control apps) but gives you a public URL.

1. **Install Ngrok**: Download from [ngrok.com](https://ngrok.com/).
2. **Run RubyBot**: Start your server as usual (`python frontend\web_server.py`).
3. **Start Tunnel**: Open a new terminal and run:
   ```bash
   ngrok http 5001
   ```
4. **Copy URL**: Ngrok will give you a link (e.g., `https://random-id.ngrok-free.app`). Open this on any device!

---

## Method 2: Hosting on Render (Web UI Only)
If you still want to host just the website on Render, you need these files. 
*Note: Voice and PC control will NOT work on Render.*

### 1. Create `requirements.txt`
Add these to a new file named `requirements.txt`:
```text
flask
flask-socketio
eventlet
gunicorn
openai
langchain
langchain-openai
python-dotenv
geocoder
```

### 2. Create `Procfile`
Create a file named `Procfile` (no extension):
```text
web: gunicorn --worker-class eventlet -w 1 frontend.web_server:app
```

### 3. Update `web_server.py`
Change the last lines to handle the Render Port:
```python
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host='0.0.0.0', port=port)
```

### 4. Deploy
1. Push your code to GitHub.
2. Connect your GitHub to [Render.com](https://render.com).
3. Add your `OPENAI_API_KEY` in the Render Environment Variables.
