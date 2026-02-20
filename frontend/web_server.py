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

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Ruby instance
ruby = Ruby()

# Override Ruby's state updates to notify the web UI
original_speak = ruby.speak
original_listen = ruby.listen

def web_speak(user_input):
    socketio.emit('state_change', {'state': 'Thinking'})
    response = original_speak(user_input)
    socketio.emit('state_change', {'state': 'Idle'})
    return response

def web_listen():
    socketio.emit('state_change', {'state': 'Listening'})
    transcript = original_listen()
    socketio.emit('state_change', {'state': 'Idle'})
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
