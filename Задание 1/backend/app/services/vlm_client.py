import base64
import json
import re
from pathlib import Path

import httpx
from app.config import settings

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "vlm_extraction.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


async def _call_ollama(model: str, prompt: str, image_b64: str) -> dict:
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(
            f"{settings.vlm_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt, "images": [image_b64]}
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_ctx": 2048,
                },
            },
        )
        response.raise_for_status()
        return response.json()


def _parse_json_loose(text: str) -> dict:
    # 1. Попытка прямого парсинга
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Попытка извлечь JSON-блок из текста
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 3. Попытка починить распространённые ошибки (одинарные кавычки, хвостовые запятые)
    try:
        fixed = text.strip()
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)  # убрать trailing comma
        fixed = fixed.replace("'", '"')               # одинарные -> двойные кавычки
        return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    # 4. Если всё сломано — вернуть пустой словарь чтобы не падать
    return {}


async def extract_with_vlm(image_bytes: bytes) -> dict:
    prompt = _load_prompt()
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    response = await _call_ollama(settings.vlm_model, prompt, image_b64)
    content = response["message"]["content"]
    return _parse_json_loose(content)
