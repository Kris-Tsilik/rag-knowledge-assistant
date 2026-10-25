"""
Базовые интерфейсы для LLM-провайдеров.
Любой новый провайдер (YandexGPT, GigaChat, OpenAI) должен реализовать эти методы.
"""
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Интерфейс для генерации векторных представлений текста."""

    @abstractmethod
    def get_embedding(self, text: str) -> list[float]:
        """Возвращает список чисел (вектор) для входного текста."""
        pass

    @abstractmethod
    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        """Опционально: пакетная обработка для экономии запросов."""
        # Дефолтная реализация — цикл по одному
        return [self.get_embedding(t) for t in texts]


class ChatProvider(ABC):
    """Интерфейс для генерации ответов текстом."""

    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        system_template: str = "",
        context_chunks: list[str] | None = None
    ) -> str:
        """
        Генерирует ответ на основе промпта, системного шаблона роли и контекста.
        
        Args:
            prompt: Вопрос пользователя.
            system_template: Шаблон системного сообщения (роль ассистента).
            context_chunks: Найденные фрагменты из базы знаний (RAG-контекст).
        """
        pass