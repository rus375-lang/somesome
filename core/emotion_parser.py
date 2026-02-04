import re

class EmotionParser:
    def parse(self, text: str):
        # Находим эмоцию
        match = re.search(r'\[EMOTION:\s*(\w+)\]', text, re.IGNORECASE)
        if match:
            # Вырезаем тег, возвращаем чистый текст
            cleaned = re.sub(r'\[EMOTION:\s*\w+\]', '', text).strip()
            return cleaned, match.group(1).lower()
        return text.strip(), "neutral"