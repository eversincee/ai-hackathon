import asyncio
from app.services.ocr_client import run_ocr_on_image, flatten_ocr_text
from app.services.vlm_client import extract_with_vlm
from app.services.llm_client import extract_with_llm
from app.services.merge import merge_extractions
from app.services.classify import classify_doc_type
from app.services.validate import validate_passport_data


async def process_page(image_bytes: bytes) -> dict:
    ocr_result = await run_ocr_on_image(image_bytes)
    ocr_text = flatten_ocr_text(ocr_result)

    vlm_task = extract_with_vlm(image_bytes)
    llm_task = extract_with_llm(ocr_text)
    vlm_json, llm_json = await asyncio.gather(vlm_task, llm_task)

    merged = merge_extractions(vlm_json, llm_json)
    doc_type = classify_doc_type(merged)
    validation = validate_passport_data(merged)

    return {
        "ocr": ocr_result,
        "vlm": vlm_json,
        "llm": llm_json,
        "merged": merged,
        "doc_type": doc_type.value,
        "validation": validation,
    }
