import numpy as np
from faster_whisper import WhisperModel
import logging

logger = logging.getLogger(__name__)

class WhisperSTT:
    def __init__(self):
        # Берём маленькую модель для скорости (скачется автоматически)
        logger.info("Загружаю Whisper (первая загрузка может занять минуту)...")
        self.model = WhisperModel(
            "base",  # Можешь потом поменять на "large-v3"
            device="cpu",  # ← У тебя пока нет CUDA настроено, берём CPU
            compute_type="int8"
        )
        
    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        # bytes -> numpy
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Распознаём
        segments, info = self.model.transcribe(audio_np, language="ru")
        
        text = " ".join([s.text for s in segments])
        return text.strip() if text else "(ничего не распознано)"