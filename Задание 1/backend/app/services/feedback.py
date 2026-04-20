import json
from datetime import datetime, timezone
from pathlib import Path


def log_correction(log_path, passport_id, scan_path, predicted, corrected):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "passport_id": passport_id,
        "scan_path": scan_path,
        "predicted": predicted,
        "corrected": corrected,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
