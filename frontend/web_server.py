from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import os
import sys
import time
import io

# Fix Windows charmap encoding issue for Unicode output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to import Ruby
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruby.ruby_mainframe import Ruby
from utiles.stt import RubySTT
from utiles.tts import RubyTTS

import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

# Initialize Ruby instance
ruby = Ruby()

# Sync Ruby's state with Web UI
def update_web_state(state):
    socketio.emit('state_change', {'state': state})

# Wrap Ruby's methods to emit events
original_speak = ruby.speak
original_listen = ruby.listen

def web_speak(user_input, play_audio=True):
    update_web_state('Thinking')
    # Disable local server audio, only send to browser
    res = original_speak(user_input, play_audio=False) 
    if res:
        audio_b64 = ruby.tts.get_speech_base64(res)
        socketio.emit('speak_audio', {'audio': audio_b64})
    update_web_state('Ready')
    return res

def web_listen():
    update_web_state('Listening')
    transcript = original_listen()
    update_web_state('Idle')
    if transcript:
        socketio.emit('new_message', {'sender': 'User', 'text': transcript})
    return transcript

ruby.speak = web_speak
ruby.listen = web_listen

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('state_change', {'state': ruby.ruby_state})
    # Greeting
    greeting = "Hello! Ruby Core is online. How can I assist you today?"
    emit('new_message', {'sender': 'Ruby', 'text': greeting})
    audio_b64 = ruby.tts.get_speech_base64(greeting)
    emit('speak_audio', {'audio': audio_b64})

@socketio.on('send_text')
def handle_text(data):
    text = data.get('text')
    print(f"Server: Received text command: {text}")
    if text:
        try:
            socketio.emit('new_message', {'sender': 'User', 'text': text})
            socketio.emit('state_change', {'state': 'Thinking'})
            
            # Process via Ruby (Assistant Logic)
            response = ruby.speak(text, play_audio=False) 
            
            # Response message and state are already handled in part by web_speak, 
            # but we can keep new_message for clarity if needed.
            # Actually, web_speak doesn't emit new_message, so we keep that.
            socketio.emit('new_message', {'sender': 'Ruby', 'text': response})
            socketio.emit('state_change', {'state': 'Ready'})
        except Exception as e:
            error_msg = f"Ruby Core Error: {str(e)}"
            print(error_msg)
            socketio.emit('new_message', {'sender': 'Ruby', 'text': error_msg})
            socketio.emit('state_change', {'state': 'Error'})

@socketio.on('mobile_audio')
def handle_mobile_audio(data):
    try:
        audio_b64 = data.get('audio')
        if not audio_b64: return
        audio_bytes = base64.b64decode(audio_b64)
        print("Processing mobile audio (Speech-to-Respond)...")
        
        # Use the unified Speech-to-Respond function
        transcript, response, response_audio = ruby.speech_to_respond(audio_bytes)
        
        if transcript:
            socketio.emit('new_message', {'sender': 'User', 'text': transcript})
            socketio.emit('new_message', {'sender': 'Ruby', 'text': response})
            # socketio.emit('speak_audio', {'audio': response_audio}) -> Removed to prevent double audio
            socketio.emit('state_change', {'state': 'Ready'})
    except Exception as e:
        print(f"Error processing mobile audio: {e}")
        socketio.emit('state_change', {'state': 'Error'})

class RubyWorker(threading.Thread):
    def __init__(self, ruby):
        super().__init__(daemon=True)
        self.ruby = ruby
        self.running = True

    def run(self):
        print("Ruby Worker Thread Started")
        while self.running:
            try:
                user_input = self.ruby.listen()
                if user_input:
                    response = self.ruby.speak(user_input)
                    socketio.emit('new_message', {'sender': 'Ruby', 'text': response})
            except Exception as e:
                try:
                    print(f"Ruby Thread Error: {e}")
                except Exception:
                    pass
                time.sleep(1)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    
    def start_worker():
        time.sleep(5) # Give the server time to bind
        print("Starting Ruby Worker...")
        worker = RubyWorker(ruby)
        worker.start()

    # threading.Thread(target=start_worker, daemon=True).start()
    
    print(f"Starting server on port {port}...")
    try:
        socketio.run(app, debug=False, host='127.0.0.1', port=port, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Startup Error: {e}")
