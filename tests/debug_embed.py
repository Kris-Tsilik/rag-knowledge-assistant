import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

CANDIDATES = [
    "text-search-document",
    "text-search-query",
    "yandexgpt-embeddings",
    "yandexgpt-embeddings-8k",
    "text-embedding",
]

for name in CANDIDATES:
    model_uri = f"emb://{YANDEX_FOLDER_ID}/{name}/latest"
    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding",
        headers={"Authorization": f"Api-Key {YANDEX_API_KEY}"},
        json={"modelUri": model_uri, "text": "тест"},
        timeout=30,
    )
    if response.status_code == 200:
        data = response.json()
        embedding = data["result"]["embedding"] if "result" in data else data["embedding"]
        print(f"[OK] {name} — размерность {len(embedding)}, ключи ответа: {list(data.keys())}")
    else:
        print(f"[--] {name} — {response.status_code}")