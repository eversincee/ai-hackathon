from app.services.validate import validate_passport_data


def test_validate_valid_trei_passport():
    data = {
        "doc_number": {"value": "TREI.421457.001 ПС", "confidence": 1.0},
        "serial_numbers": {"value": ["G4M0821"], "confidence": 1.0},
        "manufacturer_name": {"value": "АО «ТРЭИ»", "confidence": 0.9},
        "issue_date": {"value": "2024-07-10", "confidence": 0.9},
        "warranty_months": {"value": 42, "confidence": 0.95},
    }
    result = validate_passport_data(data)
    assert result.is_valid


def test_validate_unknown_doc_number_format():
    data = {
        "doc_number": {"value": "random-string", "confidence": 1.0},
        "serial_numbers": {"value": ["123"], "confidence": 1.0},
    }
    result = validate_passport_data(data)
    assert not result.is_valid
    assert "doc_number" in result.errors


def test_validate_warranty_without_issue_date():
    data = {
        "doc_number": {"value": "TREI.421457.001 ПС", "confidence": 1.0},
        "serial_numbers": {"value": ["G4M0821"], "confidence": 1.0},
        "warranty_months": {"value": 36, "confidence": 0.9},
        "issue_date": {"value": None, "confidence": 0.0},
    }
    result = validate_passport_data(data)
    assert not result.is_valid
    assert "issue_date" in result.errors


def test_trei_doc_number_must_match_trei_vendor():
    data = {
        "doc_number": {"value": "TREI.421457.001 ПС", "confidence": 1.0},
        "manufacturer_name": {"value": "АО «ТеконГруп»", "confidence": 0.9},
        "serial_numbers": {"value": ["G4M0821"], "confidence": 1.0},
    }
    result = validate_passport_data(data)
    assert not result.is_valid
