import os
import io
import tempfile
import pygame
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

# Initialize pygame mixer once at module level
pygame.mixer.init()


class RubyTTS:
    """
    Ruby Text-to-Speech (TTS) Module — powered by Edge-TTS.

    Converts text responses into spoken audio using Microsoft Edge's 
    online TTS service (Free, high quality). Plays them back using pygame.
    """

    # Mapping of BCP-47 codes to Edge-TTS voices
    language_config = {
        "en-IN": {"voice": "en-IN-PrabhatNeural", "rate": "+0%"},
        "en-US": {"voice": "en-US-AndrewNeural", "rate": "+0%"}, # High clarity male voice
        "ml-IN": {"voice": "ml-IN-SobhanaNeural", "rate": "+0%"},
        "ta-IN": {"voice": "ta-IN-ValluvarNeural", "rate": "+0%"}, # Male Tamil voice
    }

    def __init__(
        self,
        language: str = "en-IN",
        cache_dir: str = ".cache",
        speaking_rate: float = None,
        voice: str = None,
    ):
        """
        Initialize the RubyTTS instance.

        Args:
            language (str): Default language code (e.g. 'en-IN').
            cache_dir (str): Directory to store temporary audio files.
            speaking_rate (float): Not directly used by Edge-TTS in simple mode, but kept for compatibility.
            voice (str): Specific Edge-TTS voice name.
        """
        self.language_code = language
        self.cache_dir = cache_dir
        
        cfg = self.language_config.get(language, self.language_config["en-IN"])
        self.voice = voice or cfg["voice"]
        # Edge-TTS uses percentages for rate, e.g., "+0%", "-10%"
        self.rate = "+0%"

        os.makedirs(self.cache_dir, exist_ok=True)

    def update_language(self, language: str, speaking_rate: float = None):
        """
        Switch the TTS language dynamically.
        """
        print(f"TTS: Switching language to {language}")
        if language not in self.language_config:
            print(f"Language {language} not in config. Defaulting to en-IN.")
            language = "en-IN"

        self.language_code = language
        cfg = self.language_config[language]
        self.voice = cfg["voice"]

    def update_speaking_rate(self, speaking_rate: float):
        """
        Adjust speech speed. Edge-TTS expects percentage strings.
        """
        # Simple mapping: 1.0 -> +0%, 1.1 -> +10%, 0.9 -> -10%
        percent = int((speaking_rate - 1.0) * 100)
        self.rate = f"{'+' if percent >= 0 else ''}{percent}%"

    def get_current_language(self) -> str:
        return self.language_code

    def get_supported_languages(self) -> list:
        return list(self.language_config.keys())

    def _generate_audio_sync(self, text: str, output_file: str):
        """
        Run edge-tts in a dedicated thread with its own event loop.
        This avoids conflicts with Flask-SocketIO's eventlet patching of asyncio.run().
        """
        import threading

        exception_holder = []

        async def _internal():
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(output_file)

        def run_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_internal())
                loop.close()
            except Exception as e:
                exception_holder.append(e)

        t = threading.Thread(target=run_in_thread, daemon=True)
        t.start()
        t.join(timeout=30)

        if exception_holder:
            raise exception_holder[0]

    async def _generate_audio_bytes(self, text: str) -> bytes:
        """Generates audio and returns bytes directly."""
        # Try Sarvam AI TTS first if key is available
        sarvam_key = os.getenv("SARVAM_API_KEY")
        if sarvam_key and "your_" not in sarvam_key:
            try:
                import requests
                import base64
                
                url = "https://api.sarvam.ai/text-to-speech"
                
                # Mapping language for Sarvam
                lang_map = {
                    "en-IN": "en-IN",
                    "hi-IN": "hi-IN",
                    "ta-IN": "ta-IN",
                    "ml-IN": "ml-IN",
                    "te-IN": "te-IN",
                    "kn-IN": "kn-IN",
                    "gu-IN": "gu-IN",
                    "mr-IN": "mr-IN",
                    "bn-IN": "bn-IN",
                    "pa-IN": "pa-IN",
                    "or-IN": "or-IN",
                }
                sarvam_lang = lang_map.get(self.language_code, "en-IN")
                
                payload = {
                    "inputs": [text],
                    "target_language_code": sarvam_lang,
                    "speaker": "hi-IN-MadhavNeural", # Male speaker for Sarvam
                    "pitch": 0,
                    "pace": 1.0,
                    "loudness": 1.5,
                    "speech_sample_rate": 24000, # Increased from 8000 for high quality
                    "enable_preprocessing": True,
                    "model": "bulbul:v1"
                }
                
                headers = {
                    "api-subscription-key": sarvam_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    audio_b64 = response.json().get("audios", [None])[0]
                    if audio_b64:
                        print("TTS (Sarvam): Generated audio")
                        return base64.b64decode(audio_b64)
                else:
                    print(f"TTS Sarvam Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"TTS Sarvam Exception: {e}")

        # Fallback to Edge-TTS
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_speech_base64(self, text: str) -> str:
        """Returns base64 encoded audio for browser playback."""
        import base64
        import threading
        
        result = [b""]
        exception = [None]

        def run_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data = loop.run_until_complete(self._generate_audio_bytes(text))
                result[0] = data
                loop.close()
            except Exception as e:
                exception[0] = e

        t = threading.Thread(target=run_in_thread, daemon=True)
        t.start()
        t.join(timeout=30)
        
        if exception[0]:
            print(f"TTS Base64 Error: {exception[0]}")
            return ""
        
        return base64.b64encode(result[0]).decode('utf-8')

    def text_to_speech(self, text: str):
        """
        Synthesize text to speech via Edge-TTS and play it immediately on SERVER.
        (Kept for console mode backward compatibility)
        """
        if not text or not isinstance(text, str):
            return

        try:
            # Save to temp cache file
            safe_snippet = "".join(c for c in text[:8] if c.isalnum())
            cache_file = os.path.join(self.cache_dir, f"ruby_{self.language_code}_{safe_snippet}.mp3")

            self._generate_audio_sync(text, cache_file)

            if os.path.exists(cache_file):
                pygame.mixer.music.load(cache_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"TTS: Error: {e}")
        finally:
            try:
                if 'cache_file' in locals() and os.path.exists(cache_file):
                    pygame.mixer.music.unload()
                    os.remove(cache_file)
            except Exception:
                pass

    def stop(self):
        """Immediately stop any currently playing audio."""
        pygame.mixer.music.stop()
