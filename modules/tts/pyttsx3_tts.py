"""
TTS using pyttsx3 (offline, system voices)
"""
import pyttsx3
import logging
import tempfile
import wave
import io

logger = logging.getLogger(__name__)

class Pyttsx3TTS:
    """Offline TTS using Windows system voices"""
    
    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Args:
            rate: Speech rate (words per minute), 100-300
            volume: 0.0 to 1.0
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        logger.info(f"Available voices: {len(voices)}")
        
        # Try to find Russian voice, fallback to default
        russian_voice = None
        for voice in voices:
            if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                russian_voice = voice.id
                logger.info(f"Found Russian voice: {voice.name}")
                break
        
        if russian_voice:
            self.engine.setProperty('voice', russian_voice)
        else:
            logger.warning("No Russian voice found, using default")
            
    def speak(self, text: str, emotion: str = "neutral"):
        """
        Speak text aloud
        
        Args:
            text: Text to speak
            emotion: Not used in pyttsx3 (no emotion control)
        """
        logger.info(f"TTS speaking: {text[:50]}...")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def save_to_file(self, text: str, filename: str):
        """Save speech to WAV file"""
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()