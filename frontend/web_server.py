from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import os
import sys
import time

# Add parent directory to path to import Ruby
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruby.ruby_mainframe import Ruby
from utiles.stt import RubySTT
from utiles.tts import RubyTTS

import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Ruby instance
ruby = Ruby()

# Sync Ruby's state with Web UI
def update_web_state(state):
    socketio.emit('state_change', {'state': state}, broadcast=True)

# Wrap Ruby's methods to emit events
original_speak = ruby.speak
original_listen = ruby.listen

def web_speak(user_input):
    update_web_state('Thinking')
    res = original_speak(user_input)
    update_web_state('Idle')
    return res

def web_listen():
    update_web_state('Listening')
    transcript = original_listen()
    update_web_state('Idle')
    if transcript:
        socketio.emit('new_message', {'sender': 'User', 'text': transcript}, broadcast=True)
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

@socketio.on('send_text')
def handle_text(data):
    text = data.get('text')
    if text:
        socketio.emit('new_message', {'sender': 'User', 'text': text}, broadcast=True)
        response = ruby.speak(text)
        socketio.emit('new_message', {'sender': 'Ruby', 'text': response}, broadcast=True)

@socketio.on('mobile_audio')
def handle_mobile_audio(data):
    try:
        audio_b64 = data.get('audio')
        if not audio_b64: return
        audio_bytes = base64.b64decode(audio_b64)
        print("Processing mobile audio...")
        transcript = ruby.stt.transcribe_audio(audio_bytes)
        if transcript:
            socketio.emit('new_message', {'sender': 'User', 'text': transcript}, broadcast=True)
            response = ruby.speak(transcript)
            socketio.emit('new_message', {'sender': 'Ruby', 'text': response}, broadcast=True)
    except Exception as e:
        print(f"Error processing mobile audio: {e}")

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
                print(f"Ruby Thread Error: {e}")
                time.sleep(1)

if __name__ == '__main__':
    worker = RubyWorker(ruby)
    worker.start()
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
