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
    
    # Test System Health
    print("\nTesting System Health...")
    health = ruby.speak("Ruby, how is my laptop's health?")
    print(f"Ruby Answer: {health}")
    
    # Test News
    print("\nTesting News...")
    news = ruby.speak("What is the latest news?")
    print(f"Ruby Answer: {news}")
    
    print("\nTests completed.")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
