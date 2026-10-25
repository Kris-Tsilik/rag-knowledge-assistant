from pypdf import PdfReader
from pathlib import Path
import re


def _clean_page_text(text: str) -> str:
    """Убирает колонтитулы и склеивает разорванные переносом слова."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Пропускаем пустые и чисто служебные строки-обрывки
        if not stripped:
            continue
        # Убираем строки из 1-2 символов (обрывки слов после переноса)
        if len(stripped) <= 2 and not stripped.endswith("."):
            continue
        # Убираем явные колонтитулы вида "Внизу: X", "Страница N"
        if re.match(r"^(Внизу|Страница|Page)\s*[:.]?\s*\S*$", stripped):
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned)


def _glue_broken_words(text: str) -> str:
    """Склеивает слова, разорванные одиночной буквой на границе строки."""
    # Паттерн: строка кончается словом, следующая начинается с 1 строчной буквы + остаток
    # Пример: "...были\nервые динозавры" -> "...были первые динозавры" требует ручной правки,
    # но базовый случай одиночного хвоста склеиваем:
    pattern = re.compile(r"(\w)\n([а-яa-z])")
    # Склеиваем только если первая группа - конец слова, а вторая - начало следующего
    # Осторожно: не трогаем точки и знаки препинания
    result = re.sub(r"([^.,!?;:])\n([а-яa-zё])", r"\1 \2", text)
    return result


def extract_pdf_to_markdown(pdf_path: Path, output_md_path: Path):
    """Читает PDF, чистит колонтитулы и сохраняет текст в .md файл."""
    reader = PdfReader(str(pdf_path))
    parts = []

    with open(output_md_path, "w", encoding="utf-8") as md_file:
        for page_num, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned = _clean_page_text(raw_text)
            glued = _glue_broken_words(cleaned)
            if glued:
                md_file.write(f"\n## Страница {page_num}\n\n{glued}\n")

    print(f"✓ Текст извлечён и очищен: {output_md_path.name}")