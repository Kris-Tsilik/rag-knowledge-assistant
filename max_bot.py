"""
Каркас MAX-бота для RAG Knowledge Assistant.
Сетевой слой пока заглушён — заполнится после получения токена
и уточнения эндпоинтов по официальной документации developers.max.ru.

Архитектура:
  max_bot.py (этот файл)
    ├── использует CommandRouter для определения профиля по команде
    ├── использует Searcher + Generator для формирования ответа
    └── отправляет ответ через сетевой слой (заглушка пока)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.config import BASE_DIR
from src.command_router import CommandRouter


class MaxBotTransport:
    """
    Сетевой слой MAX Bot API. ЗАГЛУШКА.
    Реальные эндпоинты и формат запросов уточняются по документации
    developers.max.ru после регистрации бота через @MasterBot.
    """

    def __init__(self, token: str):
        self.token = token
        # TODO: заменить на реальный базовый URL из документации MAX
        self.api_base = "https://platform-api.max.ru/v1"

    def get_me(self) -> dict:
        """Проверка токена и получение информации о боте."""
        raise NotImplementedError(
            "Заполни этот метод после получения токена. "
            "Ожидаемый endpoint: GET /bots/getMe с заголовком Authorization: Bearer <token>"
        )

    def send_message(self, chat_id: str, text: str) -> dict:
        """Отправка текстового сообщения пользователю."""
        raise NotImplementedError(
            "Заполни этот метод после изучения документации MAX. "
            "Ожидаемый endpoint: POST /messages/send с body {chat_id, attachments/text}"
        )

    def poll_updates(self, offset: int = 0) -> tuple[list, int]:
        """
        Polling-режим: получить новые события (сообщения).
        Возвращает (список обновлений, новый offset).
        """
        raise NotImplementedError(
            "Для polling ожидается endpoint GET /updates с параметрами limit и offset. "
            "Альтернатива — webhook, но для локального запуска polling проще."
        )


class RagMaxBot:
    """Основной класс бота: связывает транспорт, роутер и RAG-пайплайн."""

    def __init__(self):
        token = os.getenv("MAX_BOT_TOKEN", "")
        if not token:
            print("⚠️ MAX_BOT_TOKEN не задан в .env — бот запустится в режиме симуляции.")
            self.simulation_mode = True
            self.transport = None
        else:
            self.simulation_mode = False
            self.transport = MaxBotTransport(token)

        self.router = CommandRouter(BASE_DIR)

    def build_welcome_message(self) -> str:
        """Формирует приветствие со списком библиотек и команд."""
        libs = self.router.list_libraries()
        lines = ["Привет! Я ассистент с базами знаний.\n\nДоступные библиотеки:\n"]
        for lib in libs:
            lines.append(f"• «{lib['display_name']}» — напиши команду: {lib['command']} <твой вопрос>")
        lines.append("\nЖду твой вопрос 🙂")
        return "\n".join(lines)

    def handle_user_message(self, chat_id: str, text: str) -> str:
        """
        Обрабатывает входящее сообщение и возвращает ответ.
        В режиме симуляции печатает шаги вместо реальной отправки.
        """
        match = self.router.resolve(text)

        if match is None:
            reply = "Не поняла команду 🤔 Напиши /help, чтобы увидеть список библиотек."
            self._deliver(chat_id, reply)
            return reply

        profile = match["profile"]
        question = match["question"]

        if not question:
            reply = (f"Библиотека «{profile['display_name']}» активна. "
                     f"Задай вопрос после команды, например:\n"
                     f"{match['matched_command']} сколько зубов у тираннозавра?")
            self._deliver(chat_id, reply)
            return reply

        # Здесь вызывается RAG-пайплайн: search_chunks + generate_answer.
        # Пока Yandex Cloud лежит, функция вернёт заглушку.
        answer = self._run_rag_pipeline(question, profile)
        self._deliver(chat_id, answer)
        return answer

    def _run_rag_pipeline(self, question: str, profile: dict) -> str:
        """
        Вызов существующего пайплайна поиска и генерации.
        """
        try:
            # 1. Добавляем папку src в путь, чтобы внутренние импорты (from config, from searcher) работали
            import sys
            from pathlib import Path
            src_path = str(Path(__file__).parent / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # 2. Импортируем реальные классы, которые есть в твоих файлах
            from searcher import Searcher
            from generator import Generator
            from utils import load_json

            # 3. Загружаем конфиг роли
            role_config = load_json(BASE_DIR / "roles" / f"{profile['role_ref']}.json")
            
            # 4. Получаем имя коллекции из роутера
            source = self.router.sources[profile["source_ref"]]
            collection = source["collection"]

            # 5. Создаём экземпляры классов (у тебя нет функций search_chunks/generate_answer, есть классы)
            # Generator внутри себя уже создаёт Searcher, но нам нужно передать профиль целиком
            # В твоем generator.py конструктор принимает profile с ключами role_data и source_data
            
            # Собираем профиль в формате, который ожидает Generator
            full_profile = {
                "role_data": role_config,
                "source_data": source
            }
            
            gen = Generator(full_profile)
            
            # 6. Вызываем метод ask у генератора
            answer = gen.ask(question)
            return answer

        except Exception as e:
            # Пока облако недоступно — понятная заглушка вместо падения
            return (f"[Режим симуляции] Вопрос: «{question}» | "
                    f"Профиль: {profile['display_name']} | "
                    f"Ошибка пайплайна: {type(e).__name__}: {e}")

    def _deliver(self, chat_id: str, text: str):
        """Отправка через транспорт или печать в консоль (симуляция)."""
        if self.simulation_mode:
            print(f"\n💬 [{chat_id}] {text}\n")
        else:
            self.transport.send_message(chat_id, text)

    def run_polling_loop(self):
        """Главный цикл обработки сообщений (polling)."""
        print("🚀 Бот запущен. Ожидание сообщений... (Ctrl+C для остановки)")
        offset = 0
        while True:
            updates, offset = self.transport.poll_updates(offset)
            for upd in updates:
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("body", {}).get("text", "")
                if chat_id and text:
                    self.handle_user_message(chat_id, text)


def simulate_dialog(bot: RagMaxBot):
    """Интерактивная симуляция диалога в консоли — замена реальному MAX до получения токена."""
    print("=" * 50)
    print("СИМУЛЯЦИЯ ДИАЛОГА С БОТОМ (без MAX API)")
    print("=" * 50)
    print(bot.build_welcome_message())
    while True:
        user_input = input("\nТы: ").strip()
        if user_input.lower() in ("/exit", "выход", "quit"):
            break
        bot.handle_user_message("demo_chat_1", user_input)


if __name__ == "__main__":
    bot = RagMaxBot()
    if bot.simulation_mode:
        simulate_dialog(bot)
    else:
        # Раскомментировать после заполнения методов транспорта и получения токена
        # bot.run_polling_loop()
        pass