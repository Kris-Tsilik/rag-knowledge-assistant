from pypdf import PdfReader
from pathlib import Path

def extract_pdf_to_markdown(pdf_path: Path, output_md_path: Path):
    """
    Читает PDF и сохраняет содержимое в .md файл.
    Добавляет заголовки страниц для лучшей навигации.
    """
    reader = PdfReader(str(pdf_path))
    
    with open(output_md_path, "w", encoding="utf-8") as md_file:
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                # Форматируем как секцию Markdown
                md_file.write(f"\n## Страница {page_num}\n\n{text}\n")
                
    print(f"✓ Текст извлечен: {output_md_path.name}")