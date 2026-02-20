import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utiles.tts import RubyTTS

class TestRubyTTS(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures. Mock external dependencies."""
        # Patch Google TTS Client
        self.patcher_client = patch('utiles.tts.texttospeech.TextToSpeechClient')
        self.mock_client_class = self.patcher_client.start()

        # Patch Pygame
        self.patcher_pygame = patch('utiles.tts.pygame')
        self.mock_pygame = self.patcher_pygame.start()
        
        # Patch OS operations to avoid file creation
        self.patcher_os = patch('utiles.tts.os')
        self.mock_os = self.patcher_os.start()

        self.tts = RubyTTS()

    def tearDown(self):
        self.patcher_client.stop()
        self.patcher_pygame.stop()
        self.patcher_os.stop()

    def test_01_initialization(self):
        """Test Case 1: Initialization Default Values"""
        print("\n[Test 1] Verifying Initialization...")
        self.assertEqual(self.tts.language_code, "en-IN")
        self.assertEqual(self.tts.speaking_rate, 0.75)
        self.mock_client_class.assert_called()

    def test_02_update_language(self):
        """Test Case 2: Language Switching Logic"""
        print("\n[Test 2] Verifying Language Update...")
        
        # Test valid switch
        self.tts.update_language("ml-IN")
        self.assertEqual(self.tts.language_code, "ml-IN")
        self.assertEqual(self.tts.voice.name, "ml-IN-Standard-A")
        
        # Test invalid switch (should fallback to en-IN)
        self.tts.update_language("invalid-lang")
        self.assertEqual(self.tts.language_code, "en-IN")

    def test_03_text_to_speech_flow(self):
        """Test Case 3: Syntax -> Write -> Play Flow"""
        print("\n[Test 3] Verifying Synthesis Flow...")
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.audio_content = b"fake_audio_bytes"
        self.tts.client.synthesize_speech.return_value = mock_response
        
        # Mock file writing
        with patch("builtins.open", mock_open()) as mock_file:
            # Mock pygame busy loop (busy once, then not busy)
            self.mock_pygame.mixer.music.get_busy.side_effect = [True, False]
            
            self.tts.text_to_speech("Hello")
            
            # 1. Check API called
            self.tts.client.synthesize_speech.assert_called()
            
            # 2. Check file written
            mock_file().write.assert_called_with(b"fake_audio_bytes")
            
            # 3. Check pygame load and play
            self.mock_pygame.mixer.music.load.assert_called()
            self.mock_pygame.mixer.music.play.assert_called()
            
            # 4. Check clean up
            self.mock_os.remove.assert_called()

    def test_04_utility_methods(self):
        """Test Case 4: Helper Methods"""
        print("\n[Test 4] Verifying Helper Methods...")
        
        # Supported languages
        langs = self.tts.get_supported_languages()
        self.assertIn("en-IN", langs)
        self.assertIn("ta-IN", langs)
        
        # Current language
        self.assertEqual(self.tts.get_current_language(), "en-IN")

    def test_05_input_validation(self):
        """Test Case 5: Input Validation"""
        print("\n[Test 5] Verifying Input Validation...")
        
        # Should handle None gracefully
        result = self.tts.text_to_speech(None)
        self.assertIsNone(result)
        self.tts.client.synthesize_speech.assert_not_called()
        
        # Should handle empty string behavior depends on implementation (if check is strictly content based)
        # Based on current code: "if not text" catches empty strings
        result = self.tts.text_to_speech("")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
