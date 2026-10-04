import json

from config import BASE_DIR

PROFILES_DIR = BASE_DIR / "profiles"


def load_profile(name):
    """Читает профиль агента по имени файла без расширения."""
    path = PROFILES_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))