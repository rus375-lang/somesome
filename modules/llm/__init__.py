from .dummy import DummyLLM
from .ollama_client import OllamaClient

def create_llm_client(config: dict):
    provider = config.get('provider', 'dummy')
    
    if provider == 'dummy':
        return DummyLLM()
    elif provider == 'ollama':
        return OllamaClient(config.get('ollama', {}))
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")