from searcher import Searcher
from yandex_gpt_client import YandexGPTClient

SCORE_THRESHOLD = 0.5


class Generator:
    """Собирает контекст из поиска и отвечает голосом роли."""

    def __init__(self, profile):
        self.persona = profile["role_data"]
        self.searcher = Searcher(profile["source_data"]["collection"])
        self.model = YandexGPTClient()

    def _system_prompt(self):
        p = self.persona
        return (
            f"Ты — {p['assistant_name']}. Твой собеседник — {p['audience_age']} лет, "
            f"он слушает ответ на слух. Тон: {p['tone']}. Отвечай {p['answer_length']}. "
            f"{p['style']}. Отвечай только на основе предоставленного контекста. "
            f"Если в контексте нет ответа, скажи: «{p['fallback']}». Не выдумывай факты."
        )

    def _build_context(self, results):
        filtered = [r for r in results if r.score >= SCORE_THRESHOLD]
        return self.searcher.format_context(filtered) if filtered else ""

    def ask(self, question):
        context = self._build_context(self.searcher.search(question))
        if not context:
            return self.persona["fallback"]
        messages = [
            {"role": "system", "text": self._system_prompt()},
            {"role": "user", "text": f"Контекст из базы знаний:\n{context}\n\nВопрос: {question}"},
        ]
        return self.model.complete(messages)