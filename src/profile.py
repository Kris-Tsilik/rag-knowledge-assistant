import json

from config import BASE_DIR

ROLES_DIR = BASE_DIR / "roles"
SOURCES_DIR = BASE_DIR / "sources"
PROFILES_DIR = BASE_DIR / "profiles"


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_role(name):
    return _read(ROLES_DIR / f"{name}.json")


def load_source(name):
    return _read(SOURCES_DIR / f"{name}.json")


def load_profile(name):
    """Собирает профиль из роли и источника."""
    profile = _read(PROFILES_DIR / f"{name}.json")
    profile["role_data"] = load_role(profile["role"])
    profile["source_data"] = load_source(profile["source"])
    return profile


def list_profiles():
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def list_sources():
    return sorted(p.stem for p in SOURCES_DIR.glob("*.json"))