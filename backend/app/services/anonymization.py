"""
The anonymization pipeline: turns identifiable SymptomLog rows (personal DB)
into k-anonymous AggregatedCaseCount rows (analytics DB).

This is the one place where personal data is read with the intent of feeding
the community-facing analytics — and it never writes anything back that could
re-identify a person. Designed to be run as a scheduled batch job (e.g. hourly
cron / Celery beat), not on the live request path.
"""
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import func

from app.core.config import settings
from app.db.database import PersonalSession, AnalyticsSession
from app.db.models import User, SymptomLog, AggregatedCaseCount


def geohash_to_centroid(geohash_cell: str) -> tuple[float, float]:
    """Decode a geohash cell to its approximate center point."""
    import geohash2
    lat, lon = geohash2.decode(geohash_cell)
    return float(lat), float(lon)


def run_anonymization_pass(bucket_hours: int = 1) -> int:
    """
    Aggregate the last `bucket_hours` of symptom logs from users who have
    opted in (shares_anonymized_data=True), grouped by (geohash, symptom_type),
    and write out only cells that meet the k-anonymity threshold.

    Returns the number of aggregated rows written.
    """
    personal_db = PersonalSession()
    analytics_db = AnalyticsSession()
    written = 0

    try:
        since = datetime.utcnow() - timedelta(hours=bucket_hours)
        time_bucket = since.replace(minute=0, second=0, microsecond=0)

        rows = (
            personal_db.query(SymptomLog, User)
            .join(User, User.id == SymptomLog.user_id)
            .filter(User.shares_anonymized_data.is_(True))
            .filter(SymptomLog.logged_at >= since)
            .filter(SymptomLog.onset_geohash.isnot(None))
            .all()
        )

        # Group by (geohash, symptom_type) — symptom_type is read directly here
        # (not decrypted free text) since it's a fixed enum/category, not PII.
        groups: dict[tuple[str, str], set[str]] = defaultdict(set)
        for symptom_log, user in rows:
            key = (symptom_log.onset_geohash, symptom_log.symptom_type_encrypted)
            groups[key].add(symptom_log.user_id)  # dedupe per user

        for (geohash_cell, symptom_type), user_ids in groups.items():
            count = len(user_ids)
            if count < settings.k_anonymity_threshold:
                continue  # too few reports — would risk re-identification

            try:
                lat, lon = geohash_to_centroid(geohash_cell)
            except Exception:
                lat, lon = None, None

            analytics_db.add(
                AggregatedCaseCount(
                    geohash_cell=geohash_cell,
                    symptom_type=symptom_type,
                    time_bucket=time_bucket,
                    report_count=count,
                    latitude=lat,
                    longitude=lon,
                )
            )
            written += 1

        analytics_db.commit()
        return written
    finally:
        personal_db.close()
        analytics_db.close()
