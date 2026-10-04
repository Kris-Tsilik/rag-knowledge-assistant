import requests

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


def synthesize(text, voice="oksana"):
    """Озвучивает текст через SpeechKit. Возвращает байты ogg или None при сбое."""
    try:
        response = requests.post(
            TTS_URL,
            headers={"Authorization": f"Api-Key {YANDEX_API_KEY}"},
            data={
                "folderId": YANDEX_FOLDER_ID,
                "text": text,
                "lang": "ru-RU",
                "voice": voice,
                "format": "oggopus",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException as error:
        print(f"[WARN] Озвучка не удалась: {error}")
        return None