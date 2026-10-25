import os
from typing import List, Dict
from pathlib import Path

from gigachat import GigaChat

class GigaChatClient:
    """Клиент для работы с GigaChat API через официальную библиотеку."""

    def __init__(self):
        credentials = os.getenv("GIGACHAT_CREDENTIALS")
        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        
        if not credentials:
            raise ValueError("GIGACHAT_CREDENTIALS не задан в .env")
        
        # Путь к сертификату Сбера (лежит в корне проекта)
        ca_bundle_path = Path(__file__).resolve().parent.parent / "russian_trusted_root_ca.cer"
        
        # Инициализация клиента с сертификатом
        # Библиотека сама получит и обновит access token
        self.client = GigaChat(
            credentials=credentials,
            scope=scope,
            ca_bundle_file=str(ca_bundle_path) if ca_bundle_path.exists() else None,
            verify_ssl_certs=True
        )

    def embed(self, text: str) -> List[float]:
        """Считает вектор локально, без обращения к платному API Сбера."""
        if not hasattr(self, "_embedding_model"):
            from fastembed import TextEmbedding
            self._embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        vectors = list(self._embedding_model.embed([text]))
        return vectors[0].tolist()

    def complete(self, messages: List[Dict[str, str]]) -> str:
        """Генерирует ответ на основе контекста и вопроса."""
        try:
            # Преобразуем формат сообщений из generator.py
            # {"role": "system", "text": "..."} → {"role": "system", "content": "..."}
            gigachat_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("text", msg.get("content", ""))
                gigachat_messages.append({"role": role, "content": content})
            
            response = self.client.chat(
                messages=gigachat_messages,
                model="GigaChat",
                temperature=0.3,
                max_tokens=512
            )
            
            # Извлекаем текст ответа
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("Пустой ответ от GigaChat chat")
        except Exception as e:
            print(f"[ERROR] Ошибка генерации ответа: {e}")
            raise