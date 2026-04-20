import uuid
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.passport import Passport, ReviewStatus
from app.schemas.passport import PassportOut, PassportPatch
from app.services.ingest import save_uploaded_file, split_pdf_to_images
from app.services.preprocess import auto_rotate_image
from app.services.extraction import process_page
from app.services.attribute_bboxes import attribute_bboxes
from app.services.feedback import log_correction

AUTO_APPROVE_THRESHOLD = 0.9

router = APIRouter(prefix="/passports", tags=["passports"])


def _merged_value(field_dict):
    """Extract the plain value from a merged field dict."""
    if isinstance(field_dict, dict) and "value" in field_dict:
        return field_dict["value"]
    return field_dict


def _merged_confidence(field_dict):
    if isinstance(field_dict, dict) and "confidence" in field_dict:
        return field_dict["confidence"]
    return 0.0


def _as_date(value):
    """LLM/VLM return dates as 'YYYY-MM-DD' strings; SQLAlchemy Date wants date objects."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "year") and hasattr(value, "month"):  # date instance
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _as_int(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(float(str(value).split()[0]))  # handles "42" and "42 мес"
    except (ValueError, TypeError, IndexError):
        return None


def _build_passport_from_merged(merged: dict, doc_type: str, scan_path: str, bboxes: dict) -> Passport:
    pid = str(uuid.uuid4())
    barcode_payload = f"pas-{pid[:8]}"

    confidences = {k: _merged_confidence(v) for k, v in merged.items() if isinstance(v, dict)}
    avg_conf = sum(confidences.values()) / max(len(confidences), 1)

    review_status = ReviewStatus.auto if avg_conf >= AUTO_APPROVE_THRESHOLD else ReviewStatus.needs_review

    return Passport(
        id=pid,
        source_scan_path=scan_path,
        source_bboxes=bboxes,
        doc_number=_merged_value(merged.get("doc_number")) or "UNKNOWN",
        doc_type=doc_type,
        product_name=_merged_value(merged.get("product_name")) or "UNKNOWN",
        product_code=_merged_value(merged.get("product_code")),
        manufacturer_name=_merged_value(merged.get("manufacturer_name")),
        manufacturer_address=_merged_value(merged.get("manufacturer_address")),
        issue_date=_as_date(_merged_value(merged.get("issue_date"))),
        package_date=_as_date(_merged_value(merged.get("package_date"))),
        acceptance_date=_as_date(_merged_value(merged.get("acceptance_date"))),
        serial_numbers=_merged_value(merged.get("serial_numbers")) or [],
        tech_specs=_merged_value(merged.get("tech_specs")) or {},
        complectness=_merged_value(merged.get("complectness")) or [],
        warranty_months=_as_int(_merged_value(merged.get("warranty_months"))),
        service_life_years=_as_int(_merged_value(merged.get("service_life_years"))),
        stamps_detected=_merged_value(merged.get("stamps_detected")) or [],
        signatures_detected=_merged_value(merged.get("signatures_detected")) or [],
        extraction_confidence=round(avg_conf, 3),
        field_confidences=confidences,
        review_status=review_status,
        barcode_payload=barcode_payload,
    )


@router.post("/ingest", response_model=list[PassportOut])
async def ingest_passport(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    filename = file.filename or f"{uuid.uuid4()}.pdf"
    scan_path = save_uploaded_file(data, Path(settings.scan_storage_dir), filename)

    if filename.lower().endswith(".pdf"):
        try:
            images = split_pdf_to_images(data)
        except (pymupdf.EmptyFileError, pymupdf.FileDataError) as e:
            raise HTTPException(status_code=400, detail=f"Cannot parse PDF: {e}")
    else:
        images = [data]

    results: list[Passport] = []
    for img_bytes in images:
        img_bytes = auto_rotate_image(img_bytes)
        page_result = await process_page(img_bytes)
        bboxes = attribute_bboxes(page_result["merged"], page_result["ocr"])
        passport = _build_passport_from_merged(
            page_result["merged"],
            page_result["doc_type"],
            str(scan_path),
            bboxes,
        )
        db.add(passport)
        results.append(passport)

    db.commit()
    for p in results:
        db.refresh(p)

    return results


@router.get("", response_model=list[PassportOut])
def list_passports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Passport).offset(skip).limit(limit).all()


@router.get("/{passport_id}", response_model=PassportOut)
def get_passport(passport_id: str, db: Session = Depends(get_db)):
    p = db.query(Passport).filter(Passport.id == passport_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passport not found")
    return p


@router.patch("/{passport_id}", response_model=PassportOut)
def patch_passport(passport_id: str, patch: PassportPatch, db: Session = Depends(get_db)):
    p = db.query(Passport).filter(Passport.id == passport_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passport not found")

    update_data = patch.model_dump(exclude_unset=True)
    if not update_data:
        return p

    predicted = {}
    corrected = {}
    for key, value in update_data.items():
        old_val = getattr(p, key, None)
        if old_val != value:
            predicted[key] = old_val
            corrected[key] = value
        setattr(p, key, value)

    if predicted:
        log_correction(
            settings.feedback_log_path,
            passport_id,
            p.source_scan_path,
            predicted,
            corrected,
        )

    db.commit()
    db.refresh(p)
    return p


@router.post("/{passport_id}/approve", response_model=PassportOut)
def approve_passport(passport_id: str, db: Session = Depends(get_db)):
    p = db.query(Passport).filter(Passport.id == passport_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passport not found")

    p.review_status = ReviewStatus.approved
    p.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(p)
    return p
