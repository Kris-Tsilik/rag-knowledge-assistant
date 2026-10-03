import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from yandex_gpt_client import YandexGPTClient

COLLECTION_NAME = "merger_guide"


def load_chunks(path: Path) -> list:
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    model_client = YandexGPTClient()

    chunks = load_chunks(DATA_DIR / "chunks.json")
    print(f"Чанков: {len(chunks)}")

    dim = len(model_client.embed("проверка размерности"))
    print(f"Размерность вектора: {dim}")

    # Пересоздаём коллекцию, чтобы повторный запуск не накапливал дубли
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"Коллекция {COLLECTION_NAME} создана")

    points = []
    for i, chunk in enumerate(chunks):
        vector = model_client.embed(chunk["text"])
        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk["source"],
                    "text": chunk["text"],
                },
            )
        )
        print(f"- эмбеддинг готов: {chunk['chunk_id']}")

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    info = client.get_collection(COLLECTION_NAME)
    print(f"Готово: точек в коллекции {COLLECTION_NAME}: {info.points_count}")


if __name__ == "__main__":
    main()