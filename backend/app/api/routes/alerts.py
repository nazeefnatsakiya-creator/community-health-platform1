"""
Real-time local alerts. New outbreak alerts are created here (e.g. by an
automated job watching AggregatedCaseCount for spikes, or by a public health
official via an admin-only endpoint) and delivered to subscribed clients via
WebSocket, keyed by the user's geohash prefix so people only get alerts
relevant to their area.
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.database import get_analytics_db
from app.db.models import OutbreakAlert
from app.schemas.schemas import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])

# In-memory connection registry keyed by geohash prefix (e.g. 5-char precision
# ≈ town-level). In production this is backed by Redis pub/sub so it works
# across multiple API server instances.
_active_connections: dict[str, list[WebSocket]] = {}


@router.get("/", response_model=List[AlertOut])
def list_recent_alerts(
    geohash_prefix: str = Query(..., min_length=3, description="User's local area geohash prefix"),
    hours: int = Query(default=72, ge=1, le=24 * 14),
    db: Session = Depends(get_analytics_db),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    rows = (
        db.query(OutbreakAlert)
        .filter(OutbreakAlert.geohash_cell.startswith(geohash_prefix))
        .filter(OutbreakAlert.created_at >= since)
        .order_by(OutbreakAlert.created_at.desc())
        .all()
    )
    return [
        AlertOut(
            id=r.id,
            geohash_cell=r.geohash_cell,
            symptom_type=r.symptom_type,
            severity_level=r.severity_level,
            message=r.message,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.websocket("/ws/{geohash_prefix}")
async def alerts_websocket(websocket: WebSocket, geohash_prefix: str):
    """Clients connect with their local-area geohash prefix and receive a
    push the moment a new alert is created for that area."""
    await websocket.accept()
    _active_connections.setdefault(geohash_prefix, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keepalive ping from client
    except WebSocketDisconnect:
        _active_connections[geohash_prefix].remove(websocket)


async def broadcast_alert(alert: OutbreakAlert):
    """Called by the alerting/anonymization background job when a new alert
    is created, to push it to every connected client in matching areas."""
    payload = AlertOut(
        id=alert.id,
        geohash_cell=alert.geohash_cell,
        symptom_type=alert.symptom_type,
        severity_level=alert.severity_level,
        message=alert.message,
        created_at=alert.created_at,
    ).model_dump_json()

    for prefix, sockets in list(_active_connections.items()):
        if alert.geohash_cell.startswith(prefix):
            for ws in list(sockets):
                try:
                    await ws.send_text(payload)
                except Exception:
                    sockets.remove(ws)
