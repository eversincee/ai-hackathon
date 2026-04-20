import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocType(str, enum.Enum):
    single = "single"
    group = "group"
    no_serial = "no_serial"


class ReviewStatus(str, enum.Enum):
    auto = "auto"
    needs_review = "needs_review"
    approved = "approved"


class Passport(Base):
    __tablename__ = "passports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_scan_path: Mapped[str] = mapped_column(String, nullable=False)
    source_bboxes: Mapped[dict] = mapped_column(JSON, default=dict)

    doc_number: Mapped[str] = mapped_column(String, nullable=False)
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType), nullable=False, default=DocType.single)
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    product_code: Mapped[str | None] = mapped_column(String, nullable=True)

    manufacturer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer_inn: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer_address: Mapped[str | None] = mapped_column(String, nullable=True)

    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    package_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    acceptance_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    serial_numbers: Mapped[list] = mapped_column(JSON, default=list)
    tech_specs: Mapped[dict] = mapped_column(JSON, default=dict)
    complectness: Mapped[list] = mapped_column(JSON, default=list)

    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    service_life_years: Mapped[int | None] = mapped_column(Integer, nullable=True)

    storage_rules: Mapped[str | None] = mapped_column(String, nullable=True)
    transport_rules: Mapped[str | None] = mapped_column(String, nullable=True)
    disposal_rules: Mapped[str | None] = mapped_column(String, nullable=True)

    stamps_detected: Mapped[list] = mapped_column(JSON, default=list)
    signatures_detected: Mapped[list] = mapped_column(JSON, default=list)

    extraction_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    field_confidences: Mapped[dict] = mapped_column(JSON, default=dict)

    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), nullable=False, default=ReviewStatus.auto
    )
    barcode_payload: Mapped[str] = mapped_column(String, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
