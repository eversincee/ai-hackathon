from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.passport import Passport
from app.models.assembly import Assembly
from app.services.barcode_gen import generate_label_pdf

router = APIRouter(prefix="/barcodes", tags=["barcodes"])


@router.get("/passport/{passport_id}/label.pdf")
def passport_label(passport_id: str, db: Session = Depends(get_db)):
    p = db.query(Passport).filter(Passport.id == passport_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Passport not found")
    pdf_bytes = generate_label_pdf(
        barcode_payload=p.barcode_payload,
        title=p.product_name or p.doc_number,
        subtitle=p.doc_number,
    )
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.get("/assembly/{assembly_id}/label.pdf")
def assembly_label(assembly_id: str, db: Session = Depends(get_db)):
    a = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assembly not found")
    pdf_bytes = generate_label_pdf(
        barcode_payload=a.barcode_payload,
        title=a.name,
        subtitle=a.kind or "",
    )
    return Response(content=pdf_bytes, media_type="application/pdf")
