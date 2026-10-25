import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import BASE_DIR
from indexer import index_source

for f in sorted((BASE_DIR / "sources").glob("*.json")):
    source = json.loads(f.read_text(encoding="utf-8"))
    print(f"Индексирую: {source.get('collection')}")
    index_source(source)

print("Готово")