"""
Security primitives:
  - Password hashing (bcrypt)
  - JWT issuing/verification for API auth
  - Field-level AES-GCM encryption for sensitive columns (symptom notes,
    medication names, mental-health entries) so a raw DB dump is unreadable.
"""
import base64
import os
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# --- Field-level encryption -------------------------------------------------
# Uses AES-256-GCM (authenticated encryption). In production the key here is
# a "data encryption key" itself encrypted by a KMS "key encryption key" —
# envelope encryption — and rotated periodically.

def _get_aesgcm() -> AESGCM:
    key = settings.field_encryption_key.encode("utf-8")[:32].ljust(32, b"0")
    return AESGCM(key)


def encrypt_field(plaintext: str) -> str:
    aesgcm = _get_aesgcm()
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_field(token: str) -> str:
    aesgcm = _get_aesgcm()
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:12], raw[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
