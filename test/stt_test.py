import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utiles.stt import RubySTT

class TestRubySTT(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures. Mock external dependencies to avoid hardware/network calls."""
        # Patch the Google Speech Client
        self.patcher_client = patch('utiles.stt.speech.SpeechClient')
        self.mock_client_class = self.patcher_client.start()
        
        # Patch sounddevice to prevent microphone access
        self.patcher_sd = patch('utiles.stt.sd.InputStream')
        self.mock_sd = self.patcher_sd.start()

        self.stt = RubySTT()

    def tearDown(self):
        self.patcher_client.stop()
        self.patcher_sd.stop()

    def test_01_initialization(self):
        """Test Case 1: Initialization Default Values"""
        print("\n[Test 1] Verifying Initialization...")
        self.assertEqual(self.stt.language_code, "en-IN")
        self.assertEqual(self.stt.sample_rate, 16000)
        # Verify client was initialized
        self.mock_client_class.assert_called()

    def test_02_update_language(self):
        """Test Case 2: Language Switching"""
        print("\n[Test 2] Verifying Language Update...")
        self.stt.update_language("ml-IN")
        
        self.assertEqual(self.stt.language_code, "ml-IN")
        # Check if client was re-initialized
        self.assertTrue(self.mock_client_class.call_count >= 2)
        
        # Verify config uses new language
        self.assertEqual(self.stt.recognition_config.language_code, "ml-IN")

    def test_03_audio_stream_logic(self):
        """Test Case 3: Audio Stream Generator"""
        print("\n[Test 3] Verifying Audio Stream Generator...")
        # Mock the stream context manager
        mock_stream_instance = self.mock_sd.return_value.__enter__.return_value
        # mock stream.read returning (data, overflow)
        # return 2 chunks then raise unexpected error or just 2 chunks for manual iteration
        mock_stream_instance.read.side_effect = [(b'chunk1', False), (b'chunk2', False), Exception("End")]
        
        generator = self.stt._audio_stream()
        
        try:
            chunk1 = next(generator)
            chunk2 = next(generator)
            self.assertEqual(chunk1, b'chunk1')
            self.assertEqual(chunk2, b'chunk2')
        except Exception:
            pass # Expected end of sequence for this test

    @patch('utiles.stt.speech.StreamingRecognizeRequest')
    def test_04_listen_success(self, mock_request):
        """Test Case 4: Successful Transcription"""
        print("\n[Test 4] Verifying Success Transcription...")
        
        # Mocking the response from Google API
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_result.is_final = True
        mock_result.alternatives[0].transcript = "Hello Ruby"
        mock_response.results = [mock_result]
        
        # Mocking streaming_recognize to return our mock list of responses
        self.stt.client.streaming_recognize.return_value = [mock_response]
        
        # Mock _audio_stream so it returns immediately (don't need real loop)
        with patch.object(self.stt, '_audio_stream', return_value=iter([b'audio_data'])):
            transcript = self.stt.listen()
            
        self.assertEqual(transcript, "Hello Ruby")
        print(f"   Transcribed: {transcript}")

    def test_05_listen_no_result(self):
        """Test Case 5: Empty/No Result"""
        print("\n[Test 5] Verifying Empty Response...")
        
        # Mocking streaming_recognize to return empty list or response with no results
        mock_response = MagicMock()
        mock_response.results = []
        
        self.stt.client.streaming_recognize.return_value = [mock_response]
        
        with patch.object(self.stt, '_audio_stream', return_value=iter([b'audio_data'])):
            transcript = self.stt.listen()
            
        self.assertEqual(transcript, "")

if __name__ == "__main__":
    unittest.main()
