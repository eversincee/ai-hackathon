import uuid
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.passport import DocType, Passport, ReviewStatus
from app.schemas.passport import PassportCreate, PassportOut


def test_passport_create_accepts_minimal():
    """PassportCreate should accept just the required base fields,
    with everything else falling back to defaults."""
    schema = PassportCreate(
        source_scan_path="/scans/minimal.pdf",
        doc_number="MIN-001",
        product_name="Minimal Widget",
    )
    assert schema.doc_number == "MIN-001"
    assert schema.doc_type == DocType.single
    assert schema.extraction_confidence == 0.0
    assert schema.review_status == ReviewStatus.auto
    assert schema.serial_numbers == []
    assert schema.tech_specs == {}
    assert schema.barcode_payload == ""


def test_passport_out_from_orm():
    """PassportOut.model_validate should successfully read from a
    real SQLAlchemy Passport ORM instance."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    passport_id = str(uuid.uuid4())
    p = Passport(
        id=passport_id,
        source_scan_path="/scans/orm_test.pdf",
        doc_number="ORM-001",
        doc_type=DocType.group,
        product_name="ORM Widget",
        serial_numbers=["SN-1"],
        tech_specs={"v": "220V"},
        extraction_confidence=0.85,
        field_confidences={"doc_number": 0.9},
        review_status=ReviewStatus.needs_review,
        barcode_payload="BC-ORM",
    )
    session.add(p)
    session.commit()
    session.refresh(p)

    out = PassportOut.model_validate(p)

    assert out.id == passport_id
    assert out.doc_number == "ORM-001"
    assert out.doc_type == DocType.group
    assert out.product_name == "ORM Widget"
    assert out.serial_numbers == ["SN-1"]
    assert out.extraction_confidence == 0.85
    assert out.review_status == ReviewStatus.needs_review
    assert out.barcode_payload == "BC-ORM"
    assert isinstance(out.created_at, datetime)
    assert out.reviewed_at is None

    session.close()
