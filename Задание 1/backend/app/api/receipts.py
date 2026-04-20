import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.receipt import ReceiptLine
from app.schemas.receipt import ReceiptLineOut

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/import")
async def import_receipts_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    count = 0
    for row in reader:
        receipt_date_val = date.fromisoformat(row["receipt_date"])
        line = ReceiptLine(
            receipt_doc_number=row["receipt_doc_number"],
            receipt_date=receipt_date_val,
            position_code=row["position_code"],
            nomenclature=row["nomenclature"],
            type_brand=row.get("type_brand") or None,
            nomenclature_code_su=row.get("nomenclature_code_su") or None,
            unit=row["unit"],
            price=float(row["price"]),
            qty_declared=int(row["qty_declared"]),
            qty_actual=int(row["qty_actual"]),
        )
        db.add(line)
        count += 1

    db.commit()
    return {"imported": count}


@router.get("", response_model=list[ReceiptLineOut])
def list_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ReceiptLine).offset(skip).limit(limit).all()
