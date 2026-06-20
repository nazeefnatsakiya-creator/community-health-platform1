"""
Central configuration. All secrets come from environment variables / a secrets
manager in production — nothing sensitive is hard-coded.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CommunityHealth Platform"
    environment: str = "development"

    # Personal-health DB holds identifiable data; analytics DB never does.
    personal_db_url: str = "postgresql://chp_user:chp_pass@localhost:5432/chp_personal"
    analytics_db_url: str = "postgresql://chp_user:chp_pass@localhost:5432/chp_analytics"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_SECRETS_MANAGER"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Field-level encryption key for symptom/medication/mental-health text.
    # In production this is fetched from a KMS (AWS KMS / GCP KMS / HashiCorp Vault),
    # never stored alongside the app config.
    field_encryption_key: str = "CHANGE_ME_32_BYTE_KEY_FROM_KMS_____"

    # Minimum count before an aggregated geo-cell is shown publicly (k-anonymity).
    k_anonymity_threshold: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
