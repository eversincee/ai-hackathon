import json
from app.services.feedback import log_correction


def test_log_correction_appends_jsonl(tmp_path):
    log_path = tmp_path / "feedback.jsonl"
    log_correction(log_path, "abc-123", "scans/x.pdf", {"doc_number": "old"}, {"doc_number": "new"})
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["passport_id"] == "abc-123"
