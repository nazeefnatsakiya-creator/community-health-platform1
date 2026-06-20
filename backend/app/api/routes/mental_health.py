from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import encrypt_field, decrypt_field
from app.db.database import get_personal_db
from app.db.models import MentalHealthLog, User
from app.schemas.schemas import MentalHealthLogCreate, MentalHealthLogOut

router = APIRouter(prefix="/mental-health", tags=["mental-health"])


@router.post("/", response_model=MentalHealthLogOut, status_code=201)
def log_mood(
    payload: MentalHealthLogCreate,
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    entry = MentalHealthLog(
        user_id=current_user.id,
        mood_score=payload.mood_score,
        notes_encrypted=encrypt_field(payload.notes) if payload.notes else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_out(entry)


@router.get("/", response_model=List[MentalHealthLogOut])
def list_mood_logs(
    db: Session = Depends(get_personal_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(MentalHealthLog)
        .filter(MentalHealthLog.user_id == current_user.id)
        .order_by(MentalHealthLog.logged_at.desc())
        .all()
    )
    return [_to_out(r) for r in rows]


def _to_out(entry: MentalHealthLog) -> MentalHealthLogOut:
    return MentalHealthLogOut(
        id=entry.id,
        mood_score=entry.mood_score,
        notes=decrypt_field(entry.notes_encrypted) if entry.notes_encrypted else None,
        logged_at=entry.logged_at,
    )
