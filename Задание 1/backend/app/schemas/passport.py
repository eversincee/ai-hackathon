from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.passport import DocType, ReviewStatus


class PassportBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_scan_path: str
    doc_number: str
    doc_type: DocType = DocType.single
    product_name: str
    product_code: str | None = None

    manufacturer_name: str | None = None
    manufacturer_inn: str | None = None
    manufacturer_address: str | None = None

    issue_date: date | None = None
    package_date: date | None = None
    acceptance_date: date | None = None

    serial_numbers: list[Any] = []
    tech_specs: dict[str, Any] = {}
    complectness: list[Any] = []

    warranty_months: int | None = None
    service_life_years: int | None = None

    storage_rules: str | None = None
    transport_rules: str | None = None
    disposal_rules: str | None = None

    stamps_detected: list[Any] = []
    signatures_detected: list[Any] = []


class PassportCreate(PassportBase):
    source_bboxes: dict[str, Any] = {}
    extraction_confidence: float = 0.0
    field_confidences: dict[str, Any] = {}
    review_status: ReviewStatus = ReviewStatus.auto
    barcode_payload: str = ""


class PassportOut(PassportBase):
    id: str
    source_bboxes: dict[str, Any] = {}
    extraction_confidence: float = 0.0
    field_confidences: dict[str, Any] = {}
    review_status: ReviewStatus = ReviewStatus.auto
    barcode_payload: str = ""
    created_at: datetime
    reviewed_at: datetime | None = None


class PassportPatch(BaseModel):
    """Editable subset of Passport fields. Unknown keys are ignored."""

    model_config = ConfigDict(extra="ignore")

    doc_number: str | None = None
    doc_type: DocType | None = None
    product_name: str | None = None
    product_code: str | None = None
    manufacturer_name: str | None = None
    manufacturer_inn: str | None = None
    manufacturer_address: str | None = None
    issue_date: date | None = None
    package_date: date | None = None
    acceptance_date: date | None = None
    serial_numbers: list[Any] | None = None
    tech_specs: dict[str, Any] | None = None
    complectness: list[Any] | None = None
    warranty_months: int | None = None
    service_life_years: int | None = None
    storage_rules: str | None = None
    transport_rules: str | None = None
    disposal_rules: str | None = None
    stamps_detected: list[Any] | None = None
    signatures_detected: list[Any] | None = None
    review_status: ReviewStatus | None = None
