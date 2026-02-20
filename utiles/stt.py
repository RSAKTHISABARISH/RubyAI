import os
import io
import wave
import tempfile
import numpy as np
import sounddevice as sd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class RubySTT:
    """
    Ruby Speech-to-Text (STT) Module — powered by OpenAI Whisper.

    Records audio from the microphone using sounddevice, then sends it
    to OpenAI's Whisper API for transcription.
    """

    def __init__(
        self,
        language_code: str = "en",
        sample_rate: int = 16_000,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_duration: float = 15.0,
    ):
        """
        Initialize the RubySTT instance.

        Args:
            language_code (str): Language hint for Whisper (e.g. 'en', 'ml', 'ta').
            sample_rate (int): Audio sample rate (default: 16000).
            silence_threshold (float): RMS level below which audio is considered silence.
            silence_duration (float): Seconds of silence before stopping recording.
            max_duration (float): Maximum recording duration in seconds.
        """
        self.language_code = language_code
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_chunks = int(silence_duration * sample_rate / 1024)
        self.max_chunks = int(max_duration * sample_rate / 1024)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def update_language(self, language_code: str):
        """
        Update the recognition language dynamically.

        Args:
            language_code (str): BCP-47 language code (e.g. 'en-IN' -> will use 'en').
        """
        # Whisper uses short codes like 'en', 'ml', 'ta'
        self.language_code = language_code.split("-")[0]

    def _record_audio(self) -> np.ndarray:
        """
        Record audio from microphone until silence is detected or max duration reached.

        Returns:
            np.ndarray: Recorded audio as a float32 array.
        """
        print("STT: Listening... (speak now)")
        frames = []
        silent_chunks = 0
        chunk_size = 1024
        started_speaking = False

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=chunk_size,
        ) as stream:
            for _ in range(self.max_chunks):
                data, _ = stream.read(chunk_size)
                rms = float(np.sqrt(np.mean(data ** 2)))

                if rms > self.silence_threshold:
                    started_speaking = True
                    silent_chunks = 0
                    frames.append(data.copy())
                elif started_speaking:
                    frames.append(data.copy())
                    silent_chunks += 1
                    if silent_chunks >= self.silence_chunks:
                        break  # Stop after enough silence

        if not frames:
            return np.zeros((0,), dtype="float32")

        return np.concatenate(frames, axis=0).flatten()

    def _audio_to_wav_bytes(self, audio: np.ndarray) -> bytes:
        """
        Convert a float32 numpy array to WAV bytes in memory.

        Args:
            audio (np.ndarray): Audio samples.

        Returns:
            bytes: WAV file bytes.
        """
        # Convert float32 to int16 PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = int16
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())
        buf.seek(0)
        return buf.read()

    def listen(self) -> str:
        """
        Record audio from the microphone and transcribe it via OpenAI Whisper.

        Returns:
            str: The transcribed text, or empty string on failure.
        """
        audio = self._record_audio()

        if len(audio) == 0:
            print("STT: No audio detected.")
            return ""

        wav_bytes = self._audio_to_wav_bytes(audio)

        # Write to a named temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.language_code,
                )
            result = transcript.text.strip()
            print(f"STT: OpenAI Whisper: {result}")
            return result
        except Exception as e:
            print(f"STT: OpenAI STT error: {e}")
            return ""
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

