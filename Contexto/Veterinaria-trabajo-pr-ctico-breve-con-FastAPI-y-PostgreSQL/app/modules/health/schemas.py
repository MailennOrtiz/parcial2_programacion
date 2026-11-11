"""Contratos de respuesta de los chequeos de salud."""

from typing import Literal

from sqlmodel import SQLModel


class LiveRead(SQLModel):
    estado: Literal["vivo"] = "vivo"


class ReadyRead(SQLModel):
    estado: Literal["listo"] = "listo"
    base_de_datos: Literal["disponible"] = "disponible"
