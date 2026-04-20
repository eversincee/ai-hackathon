from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AssemblyItem(BaseModel):
    position: int
    document_name: str
    passport_id: str | None = None
    factory_number: str | None = None
    pages_count: str | None = None
    has_certificate: bool


class AssemblyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    kind: str | None = None
    project_code: str | None = None
    factory_number: str | None = None
    items: list[AssemblyItem | dict[str, Any]] = []


class AssemblyCreate(AssemblyBase):
    pass


class AssemblyOut(AssemblyBase):
    id: str
    barcode_payload: str = ""
    created_at: datetime
