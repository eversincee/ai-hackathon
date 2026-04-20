from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReceiptLineBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    receipt_doc_number: str
    receipt_date: date

    position_code: str
    nomenclature: str
    type_brand: str | None = None
    nomenclature_code_su: str | None = None

    unit: str
    price: float
    qty_declared: int
    qty_actual: int


class ReceiptLineCreate(ReceiptLineBase):
    pass


class ReceiptLineOut(ReceiptLineBase):
    id: str
    linked_passport_ids: list[Any] = []
