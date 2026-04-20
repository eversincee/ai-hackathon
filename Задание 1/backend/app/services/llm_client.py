import json
import re
from pathlib import Path

import httpx
from app.config import settings

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "llm_extraction.txt"


def _load_prompt(ocr_text: str) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{ocr_text}", ocr_text)


async def _call_ollama(model: str, prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.llm_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.0},
            },
        )
        response.raise_for_status()
        return response.json()


def _parse_json_loose(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


async def extract_with_llm(ocr_text: str) -> dict:
    prompt = _load_prompt(ocr_text)
    response = await _call_ollama(settings.llm_model, prompt)
    content = response["message"]["content"]
    return _parse_json_loose(content)
