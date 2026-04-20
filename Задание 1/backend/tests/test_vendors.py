from app.services.vendors import load_vendors, find_vendor_by_doc_number

def test_load_vendors_returns_three():
    vendors = load_vendors()
    assert len(vendors) == 3

def test_find_vendor_trei():
    v = find_vendor_by_doc_number("TREI.421457.001 ПС")
    assert v is not None
    assert v["name"] == "АО «ТРЭИ»"

def test_find_vendor_tecon():
    v = find_vendor_by_doc_number("БНРД.434400.046ПС")
    assert v is not None
    assert v["name"] == "АО «ТеконГруп»"

def test_find_vendor_unknown_returns_none():
    assert find_vendor_by_doc_number("XYZ.999") is None
