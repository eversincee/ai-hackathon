from app.services.classify import classify_doc_type
from app.models.passport import DocType


def test_classify_single_serial():
    merged = {"serial_numbers": {"value": ["G4M0821"], "confidence": 1.0}}
    assert classify_doc_type(merged) == DocType.single


def test_classify_group_multiple_serials():
    merged = {"serial_numbers": {"value": ["3007326", "3008721", "3007819"], "confidence": 1.0}}
    assert classify_doc_type(merged) == DocType.group


def test_classify_no_serial_empty_list():
    merged = {"serial_numbers": {"value": [], "confidence": 0.0}}
    assert classify_doc_type(merged) == DocType.no_serial


def test_classify_no_serial_missing_field():
    merged = {}
    assert classify_doc_type(merged) == DocType.no_serial
