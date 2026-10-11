"""
Маршрутизация команд для MAX-бота.
Читает профили и источники, сопоставляет входную строку с командами активации.
Без обращений к внешним API — чистая логика на файлах проекта.
"""
import json
from pathlib import Path
from typing import Optional


class CommandRouter:
    """Определяет профиль и вопрос по тексту пользователя."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.profiles = {}      # profile_id -> profile_dict
        self.sources = {}       # source_id -> source_dict
        self._load_configs()

    def _load_configs(self):
        """Загружает все профили и источники из файлов проекта."""
        profiles_dir = self.base_dir / "profiles"
        sources_dir = self.base_dir / "sources"

        for f in profiles_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            pid = data.get("profile_id", f.stem)
            self.profiles[pid] = data

        for f in sources_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            sid = data.get("id", f.stem)
            self.sources[sid] = data

    def resolve(self, user_message: str) -> Optional[dict]:
        """
        Принимает сообщение пользователя.
        Возвращает dict с ключами:
          - profile: полная запись профиля (role_ref, display_name и т.д.)
          - question: текст вопроса БЕЗ команды активации
        Или None, если ни одна команда не распознана.
        """
        msg_lower = user_message.lower().strip()

        best_match = None
        best_len = 0

        for pid, profile in self.profiles.items():
            source_id = profile.get("source_ref")
            if not source_id or source_id not in self.sources:
                continue

            command = self.sources[source_id].get("command_trigger", "").lower().strip()
            if not command:
                continue

            # Ищем вхождение команды в начало сообщения
            if msg_lower.startswith(command):
                # Берём самое длинное совпадение, чтобы избежать коллизий
                if len(command) > best_len:
                    best_len = len(command)
                    remaining = user_message[len(command):].strip()
                    best_match = {
                        "profile": profile,
                        "question": remaining,
                        "matched_command": self.sources[source_id]["command_trigger"],
                    }

        return best_match

    def list_libraries(self) -> list[dict]:
        """Возвращает список доступных библиотек для приветственного сообщения."""
        result = []
        for pid, profile in self.profiles.items():
            source_id = profile.get("source_ref")
            if not source_id or source_id not in self.sources:
                continue
            source = self.sources[source_id]
            result.append({
                "display_name": profile.get("display_name", pid),
                "command": source.get("command_trigger", ""),
                "role": profile.get("role_ref", ""),
            })
        return result