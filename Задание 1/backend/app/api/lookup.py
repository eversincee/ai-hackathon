from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.passport import Passport
from app.models.assembly import Assembly

router = APIRouter(prefix="/lookup", tags=["lookup"])


@router.get("/{barcode_payload}")
def lookup_barcode(barcode_payload: str, db: Session = Depends(get_db)):
    p = db.query(Passport).filter(Passport.barcode_payload == barcode_payload).first()
    if p:
        return {"kind": "passport", "id": p.id}

    a = db.query(Assembly).filter(Assembly.barcode_payload == barcode_payload).first()
    if a:
        return {"kind": "assembly", "id": a.id}

    raise HTTPException(status_code=404, detail="Barcode not found")
