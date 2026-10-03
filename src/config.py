import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Yandex Cloud credentials
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Qdrant Cloud credentials
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Model URIs (заполним позже)
YANDEX_MODEL_URI = os.getenv("YANDEX_MODEL_URI", "")
EMBEDDING_MODEL_URI = os.getenv("EMBEDDING_MODEL_URI", "")

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Проверка наличия обязательных переменных
def validate_config():
    """Проверяет, что все обязательные переменные заданы"""
    required = [
        ("YANDEX_API_KEY", YANDEX_API_KEY),
        ("YANDEX_FOLDER_ID", YANDEX_FOLDER_ID),
        ("QDRANT_URL", QDRANT_URL),
        ("QDRANT_API_KEY", QDRANT_API_KEY),
    ]
    
    missing = [name for name, value in required if not value]
    
    if missing:
        raise ValueError(
            f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
            f"Создайте файл .env на основе .env.template и заполните значения"
        )
    
    print("✓ Конфигурация загружена успешно")

if __name__ == "__main__":
    validate_config()