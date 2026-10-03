import argparse
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunker import build_chunks
from config import DATA_DIR
from generator import Generator
from indexer import load_chunks, main as index_main
from searcher import Searcher


def cmd_index(args):
    """Индексация документа: чанкинг → эмбеддинги → загрузка в Qdrant."""
    source = DATA_DIR / args.file
    chunks = build_chunks(source)
    
    out = DATA_DIR / "chunks.json"
    import json
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Чанков создано: {len(chunks)} -> {out}")
    
    # Запуск индексации (используем функцию main из indexer.py)
    index_main()


def cmd_search(args):
    """Поиск по базе знаний."""
    query = " ".join(args.query)
    searcher = Searcher()
    results = searcher.search(query, top_k=args.top_k)
    
    print(f"Вопрос: {query}\n")
    for point in results:
        preview = point.payload["text"][:100].replace("\n", " ")
        print(f"score {point.score:.3f} | {point.payload['chunk_id']} | {preview}...")


def cmd_ask(args):
    """Задать вопрос ассистенту."""
    question = " ".join(args.question)
    generator = Generator()
    
    print(f"Вопрос: {question}\n")
    answer = generator.ask(question)
    print(f"Ответ:\n{answer}")


def main():
    parser = argparse.ArgumentParser(description="RAG-ассистент по документации")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда index
    parser_index = subparsers.add_parser("index", help="Индексировать документ")
    parser_index.add_argument("file", help="Имя файла в папке data/")
    parser_index.set_defaults(func=cmd_index)
    
    # Команда search
    parser_search = subparsers.add_parser("search", help="Поиск по базе знаний")
    parser_search.add_argument("query", nargs="+", help="Поисковый запрос")
    parser_search.add_argument("--top-k", type=int, default=3, help="Количество результатов")
    parser_search.set_defaults(func=cmd_search)
    
    # Команда ask
    parser_ask = subparsers.add_parser("ask", help="Задать вопрос ассистенту")
    parser_ask.add_argument("question", nargs="+", help="Вопрос")
    parser_ask.set_defaults(func=cmd_ask)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()