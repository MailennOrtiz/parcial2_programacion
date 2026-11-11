"""Configuración común de los contratos de entrada, no de las tablas."""

from pydantic import ConfigDict
from sqlmodel import SQLModel


class Entrada(SQLModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
