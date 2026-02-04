import io
import wave

class AudioBuffer:
    def __init__(self, sample_rate=16000):
        self.chunks = []
        self.sample_rate = sample_rate
        
    def add(self, data: bytes):
        self.chunks.append(data)
        
    def get_bytes(self) -> bytes:
        return b''.join(self.chunks)
        
    def save_wav(self, filename: str):
        """Сохранить для дебага"""
        data = self.get_bytes()
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)