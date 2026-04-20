import httpx
from app.config import settings


async def run_ocr_on_image(image_bytes: bytes) -> dict:
    async with httpx.AsyncClient(timeout=600.0) as client:
        files = {"file": ("page.png", image_bytes, "image/png")}
        response = await client.post(f"{settings.ocr_url}/ocr", files=files)
        response.raise_for_status()
        return response.json()


def flatten_ocr_text(ocr_result: dict) -> str:
    return "\n".join(line["text"] for line in ocr_result.get("text_lines", []))
