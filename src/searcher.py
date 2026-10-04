import time

from qdrant_client import QdrantClient

from config import QDRANT_API_KEY, QDRANT_URL
from yandex_gpt_client import YandexGPTClient

TOP_K = 3


class Searcher:
    """Ищет ближайшие чанки по вопросу в указанной коллекции."""

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.model = YandexGPTClient()

    def search(self, query, top_k=TOP_K):
        query_vector = self.model.embed(query)
        for attempt in range(3):
            try:
                response = self.qdrant.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    with_payload=True,
                )
                return response.points
            except Exception as error:
                print(f"[WARN] Запрос к Qdrant не прошёл (попытка {attempt + 1}): {error}")
                time.sleep(2 * (attempt + 1))
        return []

    @staticmethod
    def format_context(results):
        blocks = []
        for i, point in enumerate(results, start=1):
            blocks.append(f"[{i}] (score {point.score:.3f}) {point.payload['text']}")
        return "\n\n".join(blocks)