"""
Адаптер YandexGPT под базовые интерфейсы EmbeddingProvider и ChatProvider.
Использует существующий low-level клиент src.yandex_gpt_client.YandexGPTClient.
"""
from typing import Optional

# Импортируем твой текущий клиент
# Важно: путь должен быть правильным относительно корня проекта или пакета src
try:
    from ..yandex_gpt_client import YandexGPTClient 
except ImportError:
    # Если запуск происходит из корня проекта (python max_bot.py), относительный импорт может не сработать
    # Тогда используем абсолютный импорт через sys.path или прямой путь
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from yandex_gpt_client import YandexGPTClient

from .base import EmbeddingProvider, ChatProvider


class YandexEmbeddingProvider(EmbeddingProvider):
    """Обертка над YandexGPTClient только для эмбеддингов."""
    
    def __init__(self):
        self.client = YandexGPTClient()

    def get_embedding(self, text: str) -> list[float]:
        """
        Вызывает метод embed() твоего текущего клиента.
        Предполагается, что там уже есть retry-логика и обработка ошибок сети.
        """
        return self.client.embed(text)

    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        """
        Опциональная оптимизация. 
        Пока делаем цикл по одному, но здесь можно реализовать батч-запрос,
        если Yandex API поддерживает передачу массива текстов одним запросом.
        """
        return [self.get_embedding(t) for t in texts]


class YandexChatProvider(ChatProvider):
    """Обертка над YandexGPTClient для генерации ответов."""
    
    def __init__(self):
        self.client = YandexGPTClient()

    def generate_response(
        self, 
        prompt: str, 
        system_template: str = "",
        context_chunks: list[str] | None = None
    ) -> str:
        """
        Собирает финальный промпт и отправляет в модель.
        
        Логика сборки:
        1. System message (роль).
        2. Context (найденные чанки).
        3. User question.
        """
        messages = []
        
        if system_template:
            messages.append({"role": "system", "content": system_template})
            
        user_content_parts = []
        
        if context_chunks:
            # Форматируем контекст так, как привыкла твоя модель
            ctx_str = "\n---\n".join(context_chunks)
            user_content_parts.append(f"Контекст:\n{ctx_str}")
            
        user_content_parts.append(f"Вопрос: {prompt}")
        
        final_user_message = "\n\n".join(user_content_parts)
        messages.append({"role": "user", "content": final_user_message})
        
        # Здесь вызывается метод complete() или chat() твоего клиента.
        # ВАЖНО: Проверь сигнатуру своего YandexGPTClient. 
        # Возможно, ему нужен не список словарей, а одна строка prompt.
        # Ниже пример для одной строки (как было раньше):
        
        full_prompt_text = f"{system_template}\n\n{final_user_message}"
        
        try:
            # Допредположим, что у тебя есть метод .complete(prompt_string)
            response_text = self.client.complete(full_prompt_text)
            return response_text
        except AttributeError:
            # Если метода complete нет, попробуй другой вариант вызова,
            # который ты используешь сейчас в generator.py
            raise NotImplementedError(
                "Метод complete() не найден в YandexGPTClient. "
                "Проверь, как именно ты вызываешь LLM для ответа в текущем коде."
            )
