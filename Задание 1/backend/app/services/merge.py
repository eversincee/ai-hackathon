def _is_empty(v) -> bool:
    return v is None or v == "" or v == [] or v == {}

def _merge_scalar(a, b) -> dict:
    if _is_empty(a) and _is_empty(b):
        return {"value": None, "confidence": 0.0}
    if _is_empty(a):
        return {"value": b, "confidence": 0.7}
    if _is_empty(b):
        return {"value": a, "confidence": 0.7}
    if a == b:
        return {"value": a, "confidence": 1.0}
    return {"value": a, "confidence": 0.5, "variants": [a, b]}

def _as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    # LLM sometimes returns a single string where a list is expected
    return [v]


def _as_dict(v):
    return v if isinstance(v, dict) else {}


def _merge_list(a, b) -> dict:
    a = _as_list(a)
    b = _as_list(b)
    if a == b:
        return {"value": a, "confidence": 1.0}
    if not a:
        return {"value": b, "confidence": 0.7}
    if not b:
        return {"value": a, "confidence": 0.7}
    union = list(dict.fromkeys(a + b))
    return {"value": union, "confidence": 0.6, "variants": [a, b]}


def _merge_dict(a, b) -> dict:
    a = _as_dict(a)
    b = _as_dict(b)
    merged_value = {**a, **b}
    return {"value": merged_value, "confidence": 0.8 if a and b else 0.6}

LIST_FIELDS = {"serial_numbers", "stamps_detected", "signatures_detected", "complectness"}
DICT_FIELDS = {"tech_specs"}

def merge_extractions(a: dict, b: dict) -> dict:
    all_keys = set(a.keys()) | set(b.keys())
    result = {}
    for k in all_keys:
        va, vb = a.get(k), b.get(k)
        if k in LIST_FIELDS:
            result[k] = _merge_list(va, vb)
        elif k in DICT_FIELDS:
            result[k] = _merge_dict(va, vb)
        else:
            result[k] = _merge_scalar(va, vb)
    return result
