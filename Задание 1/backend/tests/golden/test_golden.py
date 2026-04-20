"""
Golden-set integration tests.
These require running OCR (port 8001) and Ollama (port 11434) services.
Run with: pytest tests/golden/ -v -m integration
Skip in CI with: pytest -m "not integration"
"""
import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"
GOLDEN = Path(__file__).parent

# Mark all tests as integration (skipped by default)
pytestmark = pytest.mark.integration

GOLDEN_CASES = [
    ("prilozhenie_1", "no_serial"),
    ("prilozhenie_2", "single"),
    ("prilozhenie_3", "group"),
]

def _unwrap(merged, key):
    v = merged.get(key)
    if isinstance(v, dict):
        return v.get("value")
    return v

@pytest.mark.asyncio
@pytest.mark.parametrize("name,expected_doctype", GOLDEN_CASES)
async def test_golden_extraction(name, expected_doctype):
    from app.services.ingest import split_pdf_to_images
    from app.services.preprocess import auto_rotate_image
    from app.services.extraction import process_page

    pdf_path = FIXTURES / f"{name}.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Fixture {pdf_path} not found")

    expected = json.loads((GOLDEN / f"{name}.json").read_text(encoding="utf-8"))
    pdf_bytes = pdf_path.read_bytes()
    pages = split_pdf_to_images(pdf_bytes)

    all_serials = []
    got_doc_number = None

    for page_bytes in pages:
        rotated = auto_rotate_image(page_bytes)
        result = await process_page(rotated)
        if got_doc_number is None:
            got_doc_number = _unwrap(result["merged"], "doc_number")
        serials = _unwrap(result["merged"], "serial_numbers") or []
        all_serials.extend(serials)

    seen_serials = list(dict.fromkeys(all_serials))

    # Check doc_number if expected is not null
    if expected.get("doc_number"):
        assert got_doc_number == expected["doc_number"], f"doc_number: expected {expected['doc_number']}, got {got_doc_number}"

    # Check serial recall >= 80%
    exp_serials = set(expected.get("serial_numbers", []))
    got_serials = set(seen_serials)
    if exp_serials:
        recall = len(exp_serials & got_serials) / len(exp_serials)
        assert recall >= 0.8, f"serial recall {recall:.0%} < 80% (missing: {exp_serials - got_serials})"
    else:
        assert len(seen_serials) == 0, f"expected no serials but got {seen_serials}"
