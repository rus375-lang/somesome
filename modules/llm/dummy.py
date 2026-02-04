import random

class DummyLLM:
    async def answer(self, user_text: str) -> str:
        """Фейковый ответ для теста"""
        responses = [
            "Привет! Я пока глупый, но скоро стану умным.",
            "Понял, принял, обрабатываю... (но это заглушка)",
            f"Ты сказал '{user_text[:20]}...' - интересно!",
            "[EMOTION: happy] Работает! Цепочка audio->text готова!"
        ]
        return random.choice(responses)