import json
from pathlib import Path
from unidecode import unidecode # pip install unidecode

def slugify(text: str) -> str:
    """
    Превращает 'Космос и Звезды' в 'kosmos_i_zvezdy'.
    Безопасно для имен файлов и коллекций Qdrant.
    """
    if not text:
        return ""
    # Транслитерация кириллицы в латиницу
    latin_text = unidecode(text.lower())
    # Заменяем все не-буквенно-цифровые символы на нижнее подчеркивание
    clean_text = "".join(c if c.isalnum() else "_" for c in latin_text)
    # Убираем лишние подчеркивания по краям и внутри
    while "__" in clean_text:
        clean_text = clean_text.replace("__", "_")
    return clean_text.strip("_")

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)