"""
This wrapper file ensures that hosting services like Render, 
which default to `gunicorn app:app`, can successfully locate 
and run the Flask server without requiring custom start commands.
"""
from frontend.web_server import app, socketio

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
