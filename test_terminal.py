import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ruby.ruby_mainframe import Ruby
from unittest.mock import MagicMock

# Mock TTS and STT to avoid audio issues
mock_tts = MagicMock()
mock_stt = MagicMock()

try:
    ruby = Ruby(tts=mock_tts, stt=mock_stt)
    print("Ruby initialized successfully.")
    
    # Test Terminal Command
    print("\nTesting Terminal Command...")
    output = ruby.speak("Ruby, list the files in the current folder using the terminal.")
    print(f"Ruby Answer: {output}")
    
    print("\nTests completed.")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
