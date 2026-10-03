import sys

from qdrant_client import QdrantClient

from config import QDRANT_API_KEY, QDRANT_URL
from yandex_gpt_client import YandexGPTClient

COLLECTION_NAME = "merger_guide"
TOP_K = 3


class Searcher:
    """Ищет ближайшие чанки по вопросу в Qdrant."""

    def __init__(self):
        self.qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.model = YandexGPTClient()

    def search(self, query: str, top_k: int = TOP_K) -> list:
        # Вопрос эмбеддим той же моделью, что и чанки, — иначе расстояния несравнимы
        query_vector = self.model.embed(query)
        response = self.qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )
        return response.points
    
    
    @staticmethod
    def format_context(results: list) -> str:
        blocks = []
        for i, point in enumerate(results, start=1):
            blocks.append(f"[{i}] (score {point.score:.3f}) {point.payload['text']}")
        return "\n\n".join(blocks)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Использование: python src/searcher.py "ваш вопрос"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    searcher = Searcher()
    results = searcher.search(query)

    print(f"Вопрос: {query}\n")
    for point in results:
        preview = point.payload["text"][:100].replace("\n", " ")
        print(f"score {point.score:.3f} | {point.payload['chunk_id']} | {preview}...")