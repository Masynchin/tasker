"""Модуль с конфигурационными переменными."""

import base64
import os
from pathlib import Path


def get_secket_key():
    """Получение секретного ключа."""
    key = os.getenv("SECRET_KEY").encode("u8")
    secret_key = base64.urlsafe_b64decode(key)
    return secret_key


SECRET_KEY = get_secket_key()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")

TEMPLATES_PATH = Path(__file__).parent / "templates"
STATIC_PATH = Path(__file__).parent / "static"

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRATION = os.getenv("TOKEN_EXPIRATION", 60 * 60 * 24 * 7)

CONFIRMATION_TOKEN_EXPIRATION = os.getenv(
    "CONFIRMATION_TOKEN_EXPIRATION", 60 * 60
)
CONFIRMATION_EMAIL_USERNAME = os.getenv("CONFIRMATION_EMAIL_USERNAME")
CONFIRMATION_EMAIL_PASSWORD = os.getenv("CONFIRMATION_EMAIL_PASSWORD")
