import io
import wave

import requests

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


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


def recognize(audio_bytes):
    """Распознаёт речь из записи микрофона. Возвращает текст или None."""
    try:
        if hasattr(audio_bytes, "read"):
            audio_bytes = audio_bytes.read()
        with wave.open(io.BytesIO(audio_bytes)) as wav:
            sample_rate = wav.getframerate()
            pcm = wav.readframes(wav.getnframes())
        response = requests.post(
            STT_URL,
            headers={"Authorization": f"Api-Key {YANDEX_API_KEY}"},
            params={
                "folderId": YANDEX_FOLDER_ID,
                "lang": "ru-RU",
                "format": "lpcm",
                "sampleRateHertz": sample_rate,
            },
            data=pcm,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        print(f"[STT] распознано: {data}")
        return data.get("result")
    except (requests.RequestException, wave.Error, EOFError) as error:
        print(f"[WARN] Распознавание не удалось: {error}")
        return None