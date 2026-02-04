from .pyttsx3_tts import Pyttsx3TTS

def create_tts(config: dict):
    """Factory for TTS providers"""
    provider = config.get('provider', 'pyttsx3')
    
    if provider == 'pyttsx3':
        return Pyttsx3TTS(
            rate=config.get('rate', 150),
            volume=config.get('volume', 1.0)
        )
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")