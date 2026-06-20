from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import encrypt_field, decrypt_field
from app.db.database import get_personal_db
from app.db.models import SymptomLog, User
from app.schemas.schemas import SymptomLogCreate, SymptomLogOut

router = APIRouter(prefix="/symptoms", tags=["symptoms"])


@router.post("/", response_model=SymptomLogOut, status_code=201)
def log_symptom(
    payload: SymptomLogCreate,
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    entry = SymptomLog(
        user_id=current_user.id,
        symptom_type_encrypted=payload.symptom_type,  # category, kept plain for aggregation
        severity=payload.severity,
        notes_encrypted=encrypt_field(payload.notes) if payload.notes else None,
        onset_geohash=payload.onset_geohash or current_user.home_geohash,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_out(entry)


@router.get("/", response_model=List[SymptomLogOut])
def list_symptoms(
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(SymptomLog)
        .filter(SymptomLog.user_id == current_user.id)
        .order_by(SymptomLog.logged_at.desc())
        .all()
    )
    return [_to_out(r) for r in rows]


def _to_out(entry: SymptomLog) -> SymptomLogOut:
    return SymptomLogOut(
        id=entry.id,
        symptom_type=entry.symptom_type_encrypted,
        severity=entry.severity,
        notes=decrypt_field(entry.notes_encrypted) if entry.notes_encrypted else None,
        logged_at=entry.logged_at,
    )
