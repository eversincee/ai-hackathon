import uuid
from datetime import date

from sqlalchemy import Date, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ReceiptLine(Base):
    __tablename__ = "receipt_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_doc_number: Mapped[str] = mapped_column(String, nullable=False, index=True)
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)

    position_code: Mapped[str] = mapped_column(String, nullable=False)
    nomenclature: Mapped[str] = mapped_column(String, nullable=False)
    type_brand: Mapped[str | None] = mapped_column(String, nullable=True)
    nomenclature_code_su: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    unit: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    qty_declared: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_actual: Mapped[int] = mapped_column(Integer, nullable=False)

    linked_passport_ids: Mapped[list] = mapped_column(JSON, default=list)
