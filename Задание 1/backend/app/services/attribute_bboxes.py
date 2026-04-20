def _find_line_containing(ocr_lines: list[dict], needle: str) -> list | None:
    if not needle:
        return None
    needle_lower = needle.strip().lower()
    for line in ocr_lines:
        text = line["text"].strip().lower()
        if needle_lower in text or text in needle_lower:
            return line["bbox"]
    return None


def attribute_bboxes(merged: dict, ocr: dict) -> dict[str, list]:
    lines = ocr.get("text_lines", [])
    bboxes: dict[str, list] = {}
    for field, v in merged.items():
        if not isinstance(v, dict):
            continue
        value = v.get("value")
        if value is None:
            continue
        if isinstance(value, list):
            for i, item in enumerate(value):
                b = _find_line_containing(lines, str(item))
                if b:
                    bboxes[f"{field}.{i}"] = b
        elif isinstance(value, dict):
            continue
        else:
            b = _find_line_containing(lines, str(value))
            if b:
                bboxes[field] = b
    return bboxes
