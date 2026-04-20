from functools import lru_cache
from pathlib import Path
import yaml

VENDORS_PATH = Path(__file__).parent.parent / "data" / "vendors.yaml"

@lru_cache(maxsize=1)
def load_vendors() -> list[dict]:
    with open(VENDORS_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["vendors"]

def find_vendor_by_doc_number(doc_number: str) -> dict | None:
    for v in load_vendors():
        prefix = v.get("doc_prefix", "")
        if doc_number.startswith(prefix):
            return v
    return None
