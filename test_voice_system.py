import os
import sys
sys.path.append(os.path.abspath('..'))
from utiles.tts import RubyTTS
import base64

def test_tts():
    tts = RubyTTS()
    print("Generating test audio...")
    b64 = tts.get_speech_base64("Hello, this is a test of the Ruby voice system.")
    if b64:
        print(f"Success! Generated {len(b64)} bytes of base64 audio.")
        # Save a sample to verify
        with open("test_voice.mp3", "wb") as f:
            f.write(base64.b64decode(b64))
        print("Sample saved to test_voice.mp3")
    else:
        print("Failed to generate audio.")

if __name__ == "__main__":
    test_tts()
