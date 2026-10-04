from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from chunker import build_chunks
from config import DATA_DIR, QDRANT_API_KEY, QDRANT_URL
from yandex_gpt_client import YandexGPTClient


def index_source(source):
    """Создаёт коллекцию источника и загружает эмбеддинги его чанков."""
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    model = YandexGPTClient()

    chunks = build_chunks(DATA_DIR / source["source_file"])
    collection = source["collection"]
    print(f"Чанков: {len(chunks)}")

    dim = len(model.embed("проверка размерности"))

    if client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"Коллекция {collection} создана")

    points = []
    for i, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=i,
                vector=model.embed(chunk["text"]),
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk["source"],
                    "text": chunk["text"],
                },
            )
        )
    client.upsert(collection_name=collection, points=points)
    info = client.get_collection(collection)
    print(f"Готово: точек в коллекции {collection}: {info.points_count}")