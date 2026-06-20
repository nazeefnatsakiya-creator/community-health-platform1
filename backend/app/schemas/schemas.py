from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str
    shares_anonymized_data: bool = False


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    shares_anonymized_data: bool

    class Config:
        from_attributes = True


class SymptomLogCreate(BaseModel):
    symptom_type: str
    severity: int = Field(ge=1, le=10)
    notes: Optional[str] = None
    onset_geohash: Optional[str] = None


class SymptomLogOut(BaseModel):
    id: str
    symptom_type: str
    severity: int
    notes: Optional[str]
    logged_at: datetime


class MentalHealthLogCreate(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    notes: Optional[str] = None


class MentalHealthLogOut(BaseModel):
    id: str
    mood_score: int
    notes: Optional[str]
    logged_at: datetime


class MedicationCreate(BaseModel):
    name: str
    dosage: Optional[str] = None
    schedule: Optional[str] = None


class MedicationOut(BaseModel):
    id: str
    name: str
    dosage: Optional[str]
    schedule: Optional[str]
    active: bool


class HotspotOut(BaseModel):
    geohash_cell: str
    symptom_type: str
    report_count: int
    latitude: Optional[float]
    longitude: Optional[float]
    time_bucket: datetime


class AlertOut(BaseModel):
    id: str
    geohash_cell: str
    symptom_type: str
    severity_level: str
    message: str
    created_at: datetime
