from searcher import Searcher
from yandex_gpt_client import YandexGPTClient

SCORE_THRESHOLD = 0.5  # Отсекаем чанки ниже этого порога


class Generator:
    """Собирает контекст из поиска и запрашивает ответ у YandexGPT."""

    def __init__(self):
        self.searcher = Searcher()
        self.model = YandexGPTClient()

    def _build_context(self, results: list) -> str:
        filtered = [point for point in results if point.score >= SCORE_THRESHOLD]
        if not filtered:
            return ""
        return self.searcher.format_context(filtered)

    def ask(self, question: str) -> str:
        results = self.searcher.search(question)
        context = self._build_context(results)

        if not context:
            return "В базе знаний не найдено информации для ответа на этот вопрос."

        messages = [
            {
                "role": "system",
                "text": (
                    "Ты — ассистент по документации Excel-мерджера Яндекс Маршрутов. "
                    "Отвечай только на основе предоставленного контекста. "
                    "Если в контексте нет ответа, скажи: 'В документации нет информации по этому вопросу'. "
                    "Не выдумывай факты."
                ),
            },
            {
                "role": "user",
                "text": f"Контекст из документации:\n{context}\n\nВопрос: {question}",
            },
        ]
        return self.model.complete(messages)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Использование: python src/generator.py "ваш вопрос"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    generator = Generator()

    print(f"Вопрос: {question}\n")
    answer = generator.ask(question)
    print(f"Ответ:\n{answer}")