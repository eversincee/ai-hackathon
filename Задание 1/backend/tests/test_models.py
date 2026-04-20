import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.passport import DocType, Passport, ReviewStatus


def test_passport_round_trip():
    """Create a Passport in an in-memory SQLite DB, commit, read back,
    and verify JSON fields round-trip correctly."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    passport_id = str(uuid.uuid4())
    serial_numbers = ["SN-001", "SN-002", "SN-003"]
    tech_specs = {"voltage": "220V", "power": "1500W", "weight_kg": 12.5}
    source_bboxes = {"page_1": [10, 20, 300, 400]}
    field_confidences = {"doc_number": 0.95, "product_name": 0.88}

    p = Passport(
        id=passport_id,
        source_scan_path="/scans/test.pdf",
        source_bboxes=source_bboxes,
        doc_number="TP-2024-001",
        doc_type=DocType.group,
        product_name="Test Widget",
        serial_numbers=serial_numbers,
        tech_specs=tech_specs,
        extraction_confidence=0.92,
        field_confidences=field_confidences,
        review_status=ReviewStatus.needs_review,
        barcode_payload="BARCODE123",
    )
    session.add(p)
    session.commit()

    loaded = session.get(Passport, passport_id)
    assert loaded is not None
    assert loaded.doc_number == "TP-2024-001"
    assert loaded.doc_type == DocType.group
    assert loaded.product_name == "Test Widget"
    assert loaded.review_status == ReviewStatus.needs_review
    assert loaded.extraction_confidence == 0.92

    # Verify JSON fields round-trip
    assert loaded.serial_numbers == serial_numbers
    assert loaded.tech_specs == tech_specs
    assert loaded.source_bboxes == source_bboxes
    assert loaded.field_confidences == field_confidences

    # Verify defaults
    assert loaded.stamps_detected == []
    assert loaded.signatures_detected == []
    assert loaded.complectness == []
    assert loaded.created_at is not None
    assert loaded.reviewed_at is None

    session.close()
