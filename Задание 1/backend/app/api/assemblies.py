import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.assembly import Assembly
from app.schemas.assembly import AssemblyCreate, AssemblyOut

router = APIRouter(prefix="/assemblies", tags=["assemblies"])


@router.post("", response_model=AssemblyOut)
def create_assembly(body: AssemblyCreate, db: Session = Depends(get_db)):
    aid = str(uuid.uuid4())
    barcode_payload = f"asm-{aid[:8]}"

    items_data = []
    for item in body.items:
        if isinstance(item, dict):
            items_data.append(item)
        else:
            items_data.append(item.model_dump())

    assembly = Assembly(
        id=aid,
        name=body.name,
        kind=body.kind,
        project_code=body.project_code,
        factory_number=body.factory_number,
        items=items_data,
        barcode_payload=barcode_payload,
    )
    db.add(assembly)
    db.commit()
    db.refresh(assembly)
    return assembly


@router.get("", response_model=list[AssemblyOut])
def list_assemblies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Assembly).offset(skip).limit(limit).all()


@router.get("/{assembly_id}", response_model=AssemblyOut)
def get_assembly(assembly_id: str, db: Session = Depends(get_db)):
    a = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assembly not found")
    return a


@router.delete("/{assembly_id}")
def delete_assembly(assembly_id: str, db: Session = Depends(get_db)):
    a = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assembly not found")
    db.delete(a)
    db.commit()
    return {"deleted": assembly_id}
