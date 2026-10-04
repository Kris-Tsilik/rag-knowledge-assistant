import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generator import Generator
from indexer import index_source
from profile import list_sources, load_profile, load_source
from searcher import Searcher


def cmd_index(args):
    names = [args.source] if args.source else list_sources()
    for name in names:
        print(f"== Индексация {name} ==")
        index_source(load_source(name))


def cmd_search(args):
    profile = load_profile(args.profile)
    query = " ".join(args.query)
    results = Searcher(profile["source_data"]["collection"]).search(query, top_k=args.top_k)
    print(f"Вопрос: {query}\n")
    for point in results:
        preview = point.payload["text"][:100].replace("\n", " ")
        print(f"score {point.score:.3f} | {point.payload['chunk_id']} | {preview}...")


def cmd_ask(args):
    profile = load_profile(args.profile)
    question = " ".join(args.question)
    print(f"Вопрос: {question}\n")
    print(f"Ответ:\n{Generator(profile).ask(question)}")


def main():
    parser = argparse.ArgumentParser(description="RAG-конструктор: роли, источники, профили")
    sub = parser.add_subparsers(dest="command")

    p_index = sub.add_parser("index", help="Индексировать источники")
    p_index.add_argument("--source", help="Имя источника; без него — все")
    p_index.set_defaults(func=cmd_index)

    p_search = sub.add_parser("search", help="Поиск по базе")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("--top-k", type=int, default=3)
    p_search.add_argument("--profile", default="dinopedia")
    p_search.set_defaults(func=cmd_search)

    p_ask = sub.add_parser("ask", help="Задать вопрос ассистенту")
    p_ask.add_argument("question", nargs="+")
    p_ask.add_argument("--profile", default="dinopedia")
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()