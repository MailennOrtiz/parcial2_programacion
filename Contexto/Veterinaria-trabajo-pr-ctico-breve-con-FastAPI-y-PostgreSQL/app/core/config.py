"""Configuración local, sin conexiones ni lectura de secretos al importar."""

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
            "Falta DATABASE_URL. Copiá env.example a .env y configurá una base de veterinaria."
        )
    try:
        url = make_url(valor)
    except ArgumentError:
        # No incluir el valor recibido: puede contener credenciales.
        raise RuntimeError("DATABASE_URL no tiene un formato válido.") from None
    if url.drivername != "postgresql+asyncpg" or not url.database:
        raise RuntimeError(
            "DATABASE_URL debe usar postgresql+asyncpg e indicar el nombre de la base."
        )
    return valor
