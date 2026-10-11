"""Локальный тест маршрутизатора команд. Запуск: python tests/test_command_router.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.command_router import CommandRouter

BASE_DIR = Path(__file__).resolve().parent.parent


def test_resolve_dinosaur():
    router = CommandRouter(BASE_DIR)
    result = router.resolve("Динозавры, вперед! сколько зубов у тираннозавра?")
    assert result is not None, "Команда 'Динозавры, вперед!' не распознана"
    assert result["question"] == "сколько зубов у тираннозавра?"
    assert result["profile"]["role_ref"] == "child"
    print("✓ Тест динозавров прошёл:", result)


def test_unknown_command():
    router = CommandRouter(BASE_DIR)
    result = router.resolve("привет, как дела?")
    assert result is None, "Ложное срабатывание на случайный текст"
    print("✓ Неизвестная команда корректно вернула None")


def test_list_libraries():
    router = CommandRouter(BASE_DIR)
    libs = router.list_libraries()
    assert isinstance(libs, list)
    print(f"✓ Список библиотек ({len(libs)} шт.):")
    for lib in libs:
        print(f"   • {lib['display_name']} → команда: «{lib['command']}», роль: {lib['role']}")


if __name__ == "__main__":
    test_resolve_dinosaur()
    test_unknown_command()
    test_list_libraries()
    print("\nВсе тесты пройдены успешно.")