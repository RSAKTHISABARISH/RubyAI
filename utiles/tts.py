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
        "en-IN": {"voice": "en-IN-NeerjaNeural", "rate": "+0%"},
        "ml-IN": {"voice": "ml-IN-SobhanaNeural", "rate": "+0%"},
        "ta-IN": {"voice": "ta-IN-PallaviNeural", "rate": "+0%"},
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
        """Helper to run the async edge-tts synthesis synchronously."""
        async def _internal():
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(output_file)
        
        asyncio.run(_internal())

    def text_to_speech(self, text: str):
        """
        Synthesize text to speech via Edge-TTS and play it immediately.
        """
        if not text or not isinstance(text, str):
            print("TTS: No text provided for TTS.")
            return

        try:
            print(f"TTS: Speaking: {text[:60]}{'...' if len(text) > 60 else ''}")

            # Save to temp cache file
            safe_snippet = "".join(c for c in text[:8] if c.isalnum())
            cache_file = os.path.join(self.cache_dir, f"ruby_{self.language_code}_{safe_snippet}.mp3")

            # Generate audio file
            self._generate_audio_sync(text, cache_file)

            # Play with pygame
            if os.path.exists(cache_file):
                pygame.mixer.music.load(cache_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

        except Exception as e:
            print(f"TTS: Edge-TTS error: {e}")
        finally:
            try:
                if 'cache_file' in locals() and os.path.exists(cache_file):
                    # Pygame music must be unloaded before deleting the file on Windows
                    pygame.mixer.music.unload()
                    os.remove(cache_file)
            except Exception:
                pass

    def stop(self):
        """Immediately stop any currently playing audio."""
        pygame.mixer.music.stop()
