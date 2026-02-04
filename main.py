import asyncio
import pyaudio
import numpy as np
import logging
import threading
import queue

from core.audio_buffer import AudioBuffer
from modules.stt.whisper_stt import WhisperSTT
from modules.llm import create_llm_client
from core.emotion_parser import EmotionParser
from modules.tts import create_tts
from modules.vad import create_vad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCompanion:
    def __init__(self):
        # Аудио настройки
        self.sample_rate = 16000
        self.chunk_size = 512  # 32ms @ 16kHz (оптимально для Silero VAD)
        self.channels = 1
        
        # Компоненты
        self.vad = create_vad({'threshold': 0.5, 'min_silence_duration': 0.8})
        self.stt = WhisperSTT()
        self.llm = create_llm_client({
    'provider': 'ollama',
    'ollama': {
        'model': 'qwen2.5:14b',
        'temperature': 0.7,
        'max_tokens': 150
    }
})
        self.emotion_parser = EmotionParser()
        self.tts = create_tts({'provider': 'pyttsx3', 'rate': 150})
        
        # Буферы и очереди
        self.audio_buffer = AudioBuffer()
        self.processing_queue = queue.Queue()  # Thread-safe для callback
        
        # PyAudio
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Вызывается из C-thread PyAudio"""
        if status:
            logger.debug(f"Audio status: {status}")
        
        # Просто кладём в очередь, никакой обработки в callback!
        if self.is_recording:
            self.processing_queue.put(('audio', in_data))
        
        return (None, pyaudio.paContinue)
        
    async def run(self):
        """Главный цикл"""
        logger.info("=" * 50)
        logger.info("ГОВОРИ что-нибудь (я автоматически определю конец)")
        logger.info("=" * 50)
        
        # Открываем микрофон
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.audio_callback
        )
        
        # Запускаем обработчик в отдельной корутине
        processor_task = asyncio.create_task(self._audio_processor())
        
        # Ждём первой фразы
        self.is_recording = True
        await self._wait_for_speech_end()
        
        # Останавливаем
        self.stream.stop_stream()
        self.stream.close()
        processor_task.cancel()
        
        # Обрабатываем результат
        audio_data = self.audio_buffer.get_bytes()
        if len(audio_data) > 1000:  # Минимум ~60ms
            await self._process_recognized_audio(audio_data)
        else:
            logger.warning("Слишком короткая фраза")
            
        self.pa.terminate()
        
    async def _audio_processor(self):
        """Обрабатывает аудио из очереди (async корутина)"""
        while True:
            try:
                # Не блокирующий get с таймаутом
                msg_type, data = self.processing_queue.get(timeout=0.1)
                
                if msg_type == 'audio':
                    # Добавляем в буфер
                    self.audio_buffer.add(data)
                    
                    # VAD анализ
                    result = self.vad.process_chunk(data)
                    
                    if result == "end":
                        logger.info("VAD обнаружил конец речи")
                        self.is_recording = False
                        
            except queue.Empty:
                await asyncio.sleep(0.001)  # 1ms sleep чтобы не грузить CPU
                continue
            except asyncio.CancelledError:
                break
                
    async def _wait_for_speech_end(self):
        """Ждёт пока VAD не скажет 'end'"""
        while self.is_recording:
            await asyncio.sleep(0.05)  # Проверяем каждые 50ms
            
    async def _process_recognized_audio(self, audio_data: bytes):
        """Распознаём -> LLM -> TTS"""
        logger.info("Распознаю...")
        text = self.stt.transcribe_bytes(audio_data)
        logger.info(f"Ты сказал: {text}")
        
        if not text or text == "(ничего не распознано)":
            return
            
        logger.info("Думаю...")
        response_raw, _ = await self.llm.generate(text)
        response, _ = self.emotion_parser.parse(response_raw)
        logger.info(f"AI отвечает: {response}")
        
        logger.info("Говорю...")
        self.tts.speak(response, emotion="neutral")  

if __name__ == "__main__":
    companion = SimpleCompanion()
    try:
        asyncio.run(companion.run())
    except KeyboardInterrupt:
        logger.info("Пока!")