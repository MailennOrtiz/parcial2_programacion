"""Contratos de dueños y fichas, independientes de las tablas."""

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.core.schemas import Entrada


class DuenioCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr


class DuenioUpdate(Entrada):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None

    @field_validator("nombre", "email")
    @classmethod
    def rechazar_null(cls, valor):
        # Los campos pueden omitirse, pero las columnas no admiten NULL.
        if valor is None:
            raise ValueError("El campo puede omitirse, pero no puede ser null.")
        return valor


class FichaCreate(Entrada):
    telefono: str = Field(min_length=1, max_length=40)
    direccion: str = Field(min_length=1, max_length=250)


class FichaRead(SQLModel):
    id: int
    duenio_id: int
    telefono: str
    direccion: str


class DuenioResumenRead(SQLModel):
    id: int
    nombre: str
    email: str


class DuenioRead(DuenioResumenRead):
    ficha: FichaRead | None = None
