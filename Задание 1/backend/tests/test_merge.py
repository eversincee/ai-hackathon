from app.services.merge import merge_extractions

def test_merge_agreeing_fields_high_confidence():
    a = {"doc_number": "TREI.421457.001 ПС", "product_name": "M1201E"}
    b = {"doc_number": "TREI.421457.001 ПС", "product_name": "M1201E"}
    merged = merge_extractions(a, b)
    assert merged["doc_number"]["value"] == "TREI.421457.001 ПС"
    assert merged["doc_number"]["confidence"] == 1.0

def test_merge_disagreement_low_confidence_both_variants():
    a = {"doc_number": "TREI.421457.001 ПС"}
    b = {"doc_number": "TREI.421457.002 ПС"}
    merged = merge_extractions(a, b)
    assert merged["doc_number"]["confidence"] == 0.5
    assert merged["doc_number"]["variants"] == ["TREI.421457.001 ПС", "TREI.421457.002 ПС"]

def test_merge_one_empty_takes_non_empty():
    a = {"doc_number": None}
    b = {"doc_number": "TREI.421457.001 ПС"}
    merged = merge_extractions(a, b)
    assert merged["doc_number"]["value"] == "TREI.421457.001 ПС"
    assert merged["doc_number"]["confidence"] == 0.7

def test_merge_list_field_union():
    a = {"serial_numbers": ["G4M0821"]}
    b = {"serial_numbers": ["G4M0821"]}
    merged = merge_extractions(a, b)
    assert merged["serial_numbers"]["value"] == ["G4M0821"]
    assert merged["serial_numbers"]["confidence"] == 1.0

def test_merge_dict_field():
    a = {"tech_specs": {"CPU": "ARM"}}
    b = {"tech_specs": {"RAM": "512MB"}}
    merged = merge_extractions(a, b)
    assert merged["tech_specs"]["value"] == {"CPU": "ARM", "RAM": "512MB"}
    assert merged["tech_specs"]["confidence"] == 0.8
