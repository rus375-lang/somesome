"""
Silero VAD — определение начала/конца речи
"""
import torch
import numpy as np
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class SileroVAD:
    def __init__(self, 
                 threshold: float = 0.5,
                 min_speech_duration: float = 0.25,
                 min_silence_duration: float = 0.5,
                 sample_rate: int = 16000):
        """
        Args:
            threshold: вероятность речи (0-1), выше = чувствительнее
            min_speech_duration: минимальная длина речи (сек)
            min_silence_duration: сколько тишины = конец фразы (сек)
            sample_rate: 16000 (обязательно для Silero)
        """
        self.threshold = threshold
        self.min_speech_duration = min_speech_duration
        self.min_silence_duration = min_silence_duration
        self.sample_rate = sample_rate
        
        # Загружаем модель
        logger.info("Loading Silero VAD...")
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        self.model.eval()
        
        # Состояние
        self.speech_started = False
        self.silence_duration = 0.0
        self.speech_duration = 0.0
        self.buffer = []
        
    def process_chunk(self, audio_bytes: bytes) -> str:
        """
        Обрабатывает чанк аудио (int16 -> float32 -> tensor)
        
        Returns:
            "speech" — идёт речь
            "silence" — тишина
            "end" — конец фразы (тишина > min_silence_duration)
        """
        # bytes -> numpy int16 -> float32 [-1, 1]
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # numpy -> torch tensor
        tensor = torch.from_numpy(audio_np)
        
        # Длина чанка в секундах (512 семплов @ 16kHz = 32ms)
        chunk_duration = len(audio_np) / self.sample_rate
        
        # VAD inference
        with torch.no_grad():
            speech_prob = self.model(tensor, self.sample_rate).item()
        
        is_speech = speech_prob > self.threshold
        
        if not self.speech_started:
            # Ждём начала речи
            if is_speech:
                self.speech_duration += chunk_duration
                if self.speech_duration >= self.min_speech_duration:
                    self.speech_started = True
                    logger.info("VAD: Speech started")
                    return "speech"
            return "silence"
        else:
            # Речь идёт или закончилась
            if is_speech:
                self.silence_duration = 0
                self.speech_duration += chunk_duration
                return "speech"
            else:
                self.silence_duration += chunk_duration
                if self.silence_duration >= self.min_silence_duration:
                    logger.info(f"VAD: Speech ended (duration: {self.speech_duration:.2f}s)")
                    result = "end"
                    self.reset()
                    return result
                return "speech"  # Ещё считаем речью, тишина короткая
    
    def reset(self):
        """Сброс состояния для новой фразы"""
        self.speech_started = False
        self.silence_duration = 0.0
        self.speech_duration = 0.0
        
    def get_buffer(self) -> bytes:
        """Возвращает накопленные аудио-чанки"""
        return b''.join(self.buffer)
        
    def clear_buffer(self):
        self.buffer = []