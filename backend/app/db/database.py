"""
Two separate SQLAlchemy engines: one for identifiable personal-health data,
one for anonymized community analytics. Keeping them physically separate
means there is no query path that can join personal data with analytics data.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

personal_engine = create_engine(settings.personal_db_url, pool_pre_ping=True)
analytics_engine = create_engine(settings.analytics_db_url, pool_pre_ping=True)

PersonalSession = sessionmaker(bind=personal_engine, autoflush=False, autocommit=False)
AnalyticsSession = sessionmaker(bind=analytics_engine, autoflush=False, autocommit=False)

PersonalBase = declarative_base()
AnalyticsBase = declarative_base()


def get_personal_db():
    db = PersonalSession()
    try:
        yield db
    finally:
        db.close()


def get_analytics_db():
    db = AnalyticsSession()
    try:
        yield db
    finally:
        db.close()
