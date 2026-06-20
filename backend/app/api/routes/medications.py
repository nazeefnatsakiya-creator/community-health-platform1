from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import encrypt_field, decrypt_field
from app.db.database import get_personal_db
from app.db.models import Medication, User
from app.schemas.schemas import MedicationCreate, MedicationOut

router = APIRouter(prefix="/medications", tags=["medications"])


@router.post("/", response_model=MedicationOut, status_code=201)
def add_medication(
    payload: MedicationCreate,
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    entry = Medication(
        user_id=current_user.id,
        name_encrypted=encrypt_field(payload.name),
        dosage_encrypted=encrypt_field(payload.dosage) if payload.dosage else None,
        schedule=payload.schedule,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_out(entry)


@router.get("/", response_model=List[MedicationOut])
def list_medications(
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Medication)
        .filter(Medication.user_id == current_user.id, Medication.active.is_(True))
        .all()
    )
    return [_to_out(r) for r in rows]


@router.delete("/{medication_id}", status_code=204)
def deactivate_medication(
    medication_id: str,
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(Medication)
        .filter(Medication.id == medication_id, Medication.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Medication not found")
    entry.active = False
    db.commit()


def _to_out(entry: Medication) -> MedicationOut:
    return MedicationOut(
        id=entry.id,
        name=decrypt_field(entry.name_encrypted),
        dosage=decrypt_field(entry.dosage_encrypted) if entry.dosage_encrypted else None,
        schedule=entry.schedule,
        active=entry.active,
    )
