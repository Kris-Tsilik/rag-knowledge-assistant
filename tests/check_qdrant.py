import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from qdrant_client import QdrantClient

from config import QDRANT_API_KEY, QDRANT_URL

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

collections = client.get_collections()
print("Коллекции:", [c.name for c in collections.collections])

points, _next = client.scroll(collection_name="merger_guide", limit=3, with_payload=True)
for point in points:
    preview = point.payload["text"][:60].replace("\n", " ")
    print(point.id, "|", point.payload["chunk_id"], "|", preview)