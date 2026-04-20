from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.passport import Passport, ReviewStatus
from app.services.onec_export import passports_to_csv, passports_to_commerceml_xml
from app.services.checklist_pdf import build_checklist_pdf

router = APIRouter(prefix="/export", tags=["export"])


def _approved_passports(db: Session) -> list[Passport]:
    return db.query(Passport).filter(Passport.review_status == ReviewStatus.approved).all()


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    passports = _approved_passports(db)
    csv_text = passports_to_csv(passports)
    # UTF-8 BOM so Excel / 1С on Windows render Cyrillic correctly.
    return Response(
        content=b"\xef\xbb\xbf" + csv_text.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=passports_export.csv"},
    )


@router.get("/xml")
def export_xml(db: Session = Depends(get_db)):
    passports = _approved_passports(db)
    xml_text = passports_to_commerceml_xml(passports)
    return Response(
        content=xml_text.encode("utf-8"),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=passports_export.xml"},
    )


@router.get("/checklist.pdf")
def export_checklist(db: Session = Depends(get_db)):
    passports = _approved_passports(db)
    pdf_bytes = build_checklist_pdf(passports)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=checklist.pdf"},
    )
