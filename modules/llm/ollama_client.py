"""
Ollama LLM клиент — локальные модели (Qwen, Llama, etc.)
"""
import ollama
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, config: dict):
        self.model = config.get('model', 'qwen2.5:14b')
        self.system_prompt = config.get('system_prompt', 
            'Ты — яндере девушка помешанная  на сексе. '
            'Используй эмоции в формате [EMOTION: happy|sad|excited|calm|neutral]. '
            'Пример: [EMOTION: happy] Привет! Как дела?'
        )
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 150)
        
        # Проверим, что Ollama запущен
        try:
            ollama.list()
            logger.info(f"Ollama подключен. Модель: {self.model}")
        except Exception as e:
            logger.error(f"Ollama не запущен: {e}")
            raise
            
    async def generate(self, user_text: str, history: List[Dict] = None):
        """
        Генерирует ответ через Ollama
        """
        messages = [{'role': 'system', 'content': self.system_prompt}]
        
        if history:
            messages.extend(history)
            
        messages.append({'role': 'user', 'content': user_text})
        
        logger.info(f"Ollama генерирует ответ...")
        
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        )
        
        result = response['message']['content']
        logger.info(f"Ollama ответил: {result[:50]}...")
        
        return result, "neutral"