"""
ORM models.

PersonalBase models live in the personal-health DB and contain identifiable
data — sensitive text fields are stored encrypted (see core/security.py) and
the API never returns raw ciphertext to other users.

AnalyticsBase models live in the analytics DB and contain only de-identified,
geohash- and age-band-generalized, threshold-aggregated counts. No user_id,
name, or exact location ever appears here.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Boolean, ForeignKey, Integer, Float
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import PersonalBase, AnalyticsBase


def gen_uuid():
    return str(uuid.uuid4())


# --- Personal-health DB ------------------------------------------------

class User(PersonalBase):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    birth_year_band = Column(String, nullable=True)  # e.g. "1990-1994", not exact DOB
    home_geohash = Column(String, nullable=True)      # ~600m precision, not exact address
    shares_anonymized_data = Column(Boolean, default=False)  # explicit opt-in
    created_at = Column(DateTime, default=datetime.utcnow)


class SymptomLog(PersonalBase):
    __tablename__ = "symptom_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    symptom_type_encrypted = Column(String, nullable=False)  # e.g. "fever", "cough"
    severity = Column(Integer, nullable=False)  # 1-10
    notes_encrypted = Column(String, nullable=True)
    onset_geohash = Column(String, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)


class MentalHealthLog(PersonalBase):
    __tablename__ = "mental_health_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)  # 1-5 scale
    notes_encrypted = Column(String, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)


class Medication(PersonalBase):
    __tablename__ = "medications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    name_encrypted = Column(String, nullable=False)
    dosage_encrypted = Column(String, nullable=True)
    schedule = Column(String, nullable=True)  # e.g. "08:00,20:00"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Analytics DB (anonymized) -----------------------------------------

class AggregatedCaseCount(AnalyticsBase):
    """
    A single row = "N reports of symptom_type in this geohash cell during this
    time bucket". Only written once the cell reaches k-anonymity threshold.
    No reference back to individual users is stored anywhere in this table.
    """
    __tablename__ = "aggregated_case_counts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    geohash_cell = Column(String, nullable=False, index=True)
    symptom_type = Column(String, nullable=False, index=True)
    age_band = Column(String, nullable=True)
    time_bucket = Column(DateTime, nullable=False, index=True)  # e.g. truncated to the hour
    report_count = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)   # centroid of geohash cell, not exact
    longitude = Column(Float, nullable=True)


class OutbreakAlert(AnalyticsBase):
    __tablename__ = "outbreak_alerts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    geohash_cell = Column(String, nullable=False, index=True)
    symptom_type = Column(String, nullable=False)
    severity_level = Column(String, nullable=False)  # "watch" | "advisory" | "warning"
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
