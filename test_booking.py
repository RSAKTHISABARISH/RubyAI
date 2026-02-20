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
    
    # Test Booking
    print("\nTesting Booking logic...")
    ans = ruby.speak("Ruby, book a bus ticket to Bangalore.")
    print(f"Ruby Answer: {ans}")
    
    # Test History
    print("\nTesting History logic...")
    ruby.speak("Ruby, what do I usually do?")
    
    print("\nTests completed.")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
