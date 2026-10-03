import time

import requests

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

BASE_URL = "https://llm.api.cloud.yandex.net"


class YandexGPTClient:
    """Клиент для YandexGPT API: генерация текста и эмбеддинги."""

    # Модель эмбеддинга, доступная в нашем облаке (подобрана перебором 04.10.2026)
    EMBEDDING_MODEL = "text-search-query"

    def __init__(self, api_key=YANDEX_API_KEY, folder_id=YANDEX_FOLDER_ID, max_retries=3):
        self.api_key = api_key
        self.folder_id = folder_id
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json",
        }

    def _post_with_retry(self, url, payload):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=60)
                if response.status_code != 200:
                    print(f"[WARN] Код {response.status_code}, тело: {response.text[:300]}")
                response.raise_for_status()
                return response.json()
            except requests.RequestException as error:
                last_error = error
                wait = 2 ** attempt
                print(f"[WARN] Запрос не прошёл (попытка {attempt + 1}): {error}. Пауза {wait} сек...")
                time.sleep(wait)
        raise RuntimeError(f"Не удалось выполнить запрос после {self.max_retries} попыток: {last_error}")

    def complete(self, messages, temperature=0.3, max_tokens="2000"):
        """Генерация текста (chat completion)."""
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
            "messages": messages,
        }
        data = self._post_with_retry(f"{BASE_URL}/foundationModels/v1/completion", payload)
        return data["result"]["alternatives"][0]["message"]["text"]

    def embed(self, text):
        """Эмбеддинг текста. Чанки и запросы эмбеддим одной моделью — так поиск консистентен."""
        payload = {
            "modelUri": f"emb://{self.folder_id}/{self.EMBEDDING_MODEL}/latest",
            "text": text,
        }
        data = self._post_with_retry(f"{BASE_URL}/foundationModels/v1/textEmbedding", payload)
        return data["embedding"] if "embedding" in data else data["result"]["embedding"]


if __name__ == "__main__":
    client = YandexGPTClient()

    answer = client.complete([
        {"role": "user", "text": "Ответь одним предложением: что такое RAG?"},
    ])
    print("Ответ модели:", answer)

    vector = client.embed("Тестовый текст для проверки эмбеддинга")
    print("Размерность вектора:", len(vector))