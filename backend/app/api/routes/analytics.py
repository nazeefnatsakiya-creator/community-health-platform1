from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_analytics_db
from app.db.models import AggregatedCaseCount
from app.schemas.schemas import HotspotOut

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/hotspots", response_model=List[HotspotOut])
def get_hotspots(
    hours: int = Query(default=24, ge=1, le=24 * 30),
    symptom_type: Optional[str] = None,
    db: Session = Depends(get_analytics_db),
):
    """
    Public, anonymized endpoint — no auth required, no personal data returned.
    Powers the community trend map and hotspot view.
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(AggregatedCaseCount).filter(AggregatedCaseCount.time_bucket >= since)
    if symptom_type:
        q = q.filter(AggregatedCaseCount.symptom_type == symptom_type)

    rows = q.order_by(AggregatedCaseCount.time_bucket.desc()).limit(2000).all()
    return [
        HotspotOut(
            geohash_cell=r.geohash_cell,
            symptom_type=r.symptom_type,
            report_count=r.report_count,
            latitude=r.latitude,
            longitude=r.longitude,
            time_bucket=r.time_bucket,
        )
        for r in rows
    ]


@router.get("/trends")
def get_trends(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_analytics_db),
):
    """Daily total report counts per symptom type, for the trend chart."""
    from sqlalchemy import func

    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date_trunc("day", AggregatedCaseCount.time_bucket).label("day"),
            AggregatedCaseCount.symptom_type,
            func.sum(AggregatedCaseCount.report_count).label("total"),
        )
        .filter(AggregatedCaseCount.time_bucket >= since)
        .group_by("day", AggregatedCaseCount.symptom_type)
        .order_by("day")
        .all()
    )
    return [
        {"day": r.day.isoformat(), "symptom_type": r.symptom_type, "total": int(r.total)}
        for r in rows
    ]
