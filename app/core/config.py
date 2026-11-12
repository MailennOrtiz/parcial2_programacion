"""Configuración local: lee la URL de la base desde el entorno."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


RUTA_ENV = Path(__file__).resolve().parents[2] / ".env"


def obtener_database_url() -> str:
    """El entorno tiene prioridad sobre el .env ubicado en la raíz del proyecto."""
    load_dotenv(RUTA_ENV, override=False)
    valor = os.getenv("DATABASE_URL", "").strip()
    if not valor:
        raise RuntimeError(
            "Falta DATABASE_URL. Copiá env.example a .env y configurá la base."
        )
    try:
        url = make_url(valor)
    except ArgumentError:
        raise RuntimeError("DATABASE_URL no tiene un formato válido.") from None
    if url.drivername != "postgresql+asyncpg" or not url.database:
        raise RuntimeError(
            "DATABASE_URL debe usar postgresql+asyncpg e indicar el nombre de la base."
        )
    return valor


def obtener_sql_echo() -> bool:
    load_dotenv(RUTA_ENV, override=False)
    valor = os.getenv("SQL_ECHO", "false").strip().lower()
    return valor in {"1", "true", "yes", "si", "on"}


def obtener_cors_origins() -> list[str]:
    """Lee orígenes separados por comas; por defecto no habilita ninguno."""
    load_dotenv(RUTA_ENV, override=False)
    valor = os.getenv("CORS_ORIGINS", "")
    return [origen.strip() for origen in valor.split(",") if origen.strip()]
