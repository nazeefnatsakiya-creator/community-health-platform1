# CommunityHealth — Public Health Platform

A community-driven public health platform: personal health dashboards, anonymized
community trend visualizations, and real-time local outbreak alerts. Designed to be
accessible to all ages and devices, and to scale nationally by 2027.

## 1. System overview

```
                         ┌──────────────────────┐
                         │   Mobile / Web App     │  React + PWA (offline-first,
                         │   (any device)         │  large-text & screen-reader modes)
                         └──────────┬────────────┘
                                    │ HTTPS / WSS (TLS 1.3)
                         ┌──────────▼────────────┐
                         │   API Gateway          │  authn, rate limiting,
                         │   (FastAPI + Nginx)    │  request signing
                         └──────────┬────────────┘
            ┌───────────────────────┼───────────────────────┐
   ┌────────▼────────┐   ┌──────────▼─────────┐   ┌──────────▼─────────┐
   │ Personal Health   │   │ Community Analytics │   │ Alerting Service    │
   │ Service           │   │ Service              │   │ (real-time, geo)    │
   │ (symptoms, meds,  │   │ (aggregation,        │   │ push/SMS/WebSocket  │
   │ mental health log)│   │ anonymization,       │   │                      │
   │                    │   │ hotspot detection)   │   │                      │
   └────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘
            │                          │                          │
   ┌────────▼──────────┐   ┌──────────▼──────────┐   ┌───────────▼─────────┐
   │ Postgres (per-user │   │ Postgres + PostGIS   │   │ Redis (pub/sub,      │
   │ encrypted at rest, │   │ (aggregated, k-      │   │ geo-indexed alert    │
   │ row-level security)│   │ anonymized, no PII)  │   │ delivery queue)      │
   └────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

Three services share one API gateway but own separate databases, so a breach or bug
in the analytics service can never expose identifiable personal health records.

## 2. Core features → implementation

| Feature | How it's built |
|---|---|
| Personal dashboard (symptoms, mental health, meds) | `backend/app/api/routes/{symptoms,mental_health,medications}.py`, encrypted per-user records, `frontend/src/pages/Dashboard.jsx` |
| Community trends & outbreak hotspots | `analytics` service aggregates de-identified, k-anonymized reports by geohash; `frontend/src/components/HotspotMap.jsx` |
| Real-time local alerts | `alerts` service subscribes to new aggregated case clusters, pushes via WebSocket/Web Push/SMS based on user's geofence; `backend/app/api/routes/alerts.py` |

## 3. Privacy & security (by design, not bolted on)

- **Encryption in transit**: TLS 1.3 everywhere; mutual TLS between internal services.
- **Encryption at rest**: AES-256 for personal-health-service database; field-level
  encryption (envelope encryption via KMS) for symptom text, medication names, and
  mental-health notes specifically, so even a DB dump is unreadable without the KMS key.
- **Anonymization pipeline**: personal data never reaches the analytics DB directly.
  A one-way pipeline strips identifiers, generalizes location to a geohash (~600m
  cells), generalizes age to 5-year bands, and only emits aggregated counts once a
  cell reaches a minimum threshold (k-anonymity, k≥5) to prevent re-identification
  in sparsely populated areas.
- **Access control**: row-level security in Postgres so a user's API token can only
  ever read their own rows; staff/clinician access is role-based, scoped, and logged.
- **Compliance posture**: architecture maps to HIPAA (US), GDPR (EU/UK), and POPIA-style
  regimes — audit logging of all access to identifiable data, data subject export/delete
  endpoints, configurable data-retention windows, and a documented Data Processing
  Agreement template for any partner health authority. (This is an engineering
  scaffold, not a legal compliance certification — a compliance review/BAA process
  with qualified counsel is required before handling real patient data.)
- **Consent**: explicit, granular opt-in for whether a user's anonymized data
  contributes to community trend analytics, separate from using their own dashboard.

## 4. Scalability & device compatibility

- Stateless API services behind a gateway → horizontal autoscaling (Kubernetes HPA,
  see `infra/`).
- Read-heavy analytics queries served from a materialized, pre-aggregated table
  refreshed on a schedule, not computed live per request.
- Frontend is a installable Progressive Web App: works on low-end Android phones,
  desktop browsers, and supports offline symptom logging that syncs when back online
  — important for low-connectivity rural areas.
- Accessibility: large-text mode, high-contrast theme, multi-language support, and
  screen-reader-tested components so the platform is usable by older adults and
  people with disabilities, not just digitally fluent users.

## 5. Repo layout

```
backend/app/
  core/        config, security/encryption helpers, auth
  db/          SQLAlchemy models, session management
  api/routes/  symptoms, mental_health, medications, alerts, analytics
  schemas/     Pydantic request/response models
  services/    anonymization + hotspot detection logic
frontend/src/
  pages/       Dashboard, CommunityTrends, Alerts
  components/  SymptomTracker, MedicationList, MoodLog, HotspotMap, AlertBanner
infra/         docker-compose for local dev; notes for k8s production deploy
```

## 6. Roadmap toward 2027 launch

1. **Now → +3 mo**: harden auth (MFA), finish anonymization pipeline, pilot with one
   community health partner.
2. **+3 → +9 mo**: clinician/public-health-authority dashboard, SMS alerts for
   feature-phone users, accessibility audit.
3. **+9 → +18 mo**: multi-region deployment, formal compliance review (HIPAA/GDPR),
   load testing at city scale.
4. **+18 → 24 mo**: national rollout, integration with public health authority
   reporting systems, post-launch security audit.

## 7. Getting started (local dev)

```bash
docker compose up --build
# API:        http://localhost:8000/docs
# Frontend:   http://localhost:5173
```

See `backend/requirements.txt` and `frontend/package.json` for dependencies.
