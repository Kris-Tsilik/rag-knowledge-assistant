import json
import sys
from pathlib import Path

from config import DATA_DIR

CHUNK_SIZE = 800      # целевой размер чанка в символах
CHUNK_OVERLAP = 100   # перекрытие соседних чанков


def read_text(path: Path) -> str:
    """Читает .txt и .md файлы."""
    if path.suffix.lower() in (".txt", ".md"):
        return path.read_text(encoding="utf-8")
    raise ValueError(f"Неподдерживаемый формат {path.suffix}: используйте .txt или .md")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Режет текст окнами с перекрытием, границу дотягивает до конца предложения."""
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            for sep in ("\n\n", ". ", "! ", "? "):
                pos = text.rfind(sep, start + chunk_size // 2, end)
                if pos != -1:
                    end = pos + len(sep)
                    break
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def build_chunks(source_path: Path) -> list:
    raw = chunk_text(read_text(source_path))
    return [
        {
            "chunk_id": f"{source_path.stem}_{i:03d}",
            "source": source_path.name,
            "text": chunk,
        }
        for i, chunk in enumerate(raw)
    ]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python src/chunker.py <имя файла в data/>")
        sys.exit(1)

    source = DATA_DIR / sys.argv[1]
    chunks = build_chunks(source)

    out = DATA_DIR / "chunks.json"
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Чанков: {len(chunks)} -> {out}")
    for chunk in chunks[:3]:
        preview = chunk["text"][:80].replace("\n", " ")
        print(f"- {chunk['chunk_id']} | {preview}...")