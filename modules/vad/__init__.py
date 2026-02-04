from .silero_vad import SileroVAD

def create_vad(config: dict):
    return SileroVAD(
        threshold=config.get('threshold', 0.5),
        min_speech_duration=config.get('min_speech_duration', 0.25),
        min_silence_duration=config.get('min_silence_duration', 0.5)
    )