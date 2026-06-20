from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, symptoms, mental_health, medications, analytics, alerts
from app.core.config import settings
from app.db.database import personal_engine, analytics_engine
from app.db.database import PersonalBase, AnalyticsBase

app = FastAPI(
    title=settings.app_name,
    description=(
        "Community-driven public health platform API: personal health dashboards, "
        "anonymized community trend analytics, and real-time local outbreak alerts."
    ),
    version="0.1.0",
)

# In production, restrict to the actual frontend origin(s) — not "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # In production, use Alembic migrations instead of create_all.
    PersonalBase.metadata.create_all(bind=personal_engine)
    AnalyticsBase.metadata.create_all(bind=analytics_engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(symptoms.router)
app.include_router(mental_health.router)
app.include_router(medications.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
