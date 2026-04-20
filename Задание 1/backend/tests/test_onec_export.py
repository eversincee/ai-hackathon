from app.services.onec_export import passports_to_csv, passports_to_commerceml_xml
from app.services.checklist_pdf import build_checklist_pdf
from app.models.passport import Passport, DocType, ReviewStatus

def _sample_passport():
    return Passport(
        id="abc-123",
        source_scan_path="scans/x.pdf",
        doc_number="TREI.421457.001 ПС",
        doc_type=DocType.single,
        product_name="Мастер-модуль M1201E",
        product_code="M1201E-0",
        serial_numbers=["G4M0821"],
        tech_specs={},
        barcode_payload="paspt-abc123",
        review_status=ReviewStatus.approved,
    )

def test_csv_export_has_columns():
    csv_text = passports_to_csv([_sample_passport()])
    assert "Номенклатура" in csv_text
    assert "M1201E" in csv_text

def test_commerceml_xml_is_valid():
    xml_text = passports_to_commerceml_xml([_sample_passport()])
    assert "<КоммерческаяИнформация" in xml_text
    assert "<Товар>" in xml_text
    assert "M1201E" in xml_text

def test_checklist_pdf_returns_pdf():
    pdf = build_checklist_pdf([_sample_passport()])
    assert isinstance(pdf, bytes)
    assert pdf[:4] == b"%PDF"
