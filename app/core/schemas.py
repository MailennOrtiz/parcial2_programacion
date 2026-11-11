"""Bases compartidas de los contratos de la API."""

from pydantic import ConfigDict
from sqlmodel import SQLModel


class Entrada(SQLModel):
    model_config = ConfigDict(extra="forbid")


class Lectura(SQLModel):
    model_config = ConfigDict(from_attributes=True)
