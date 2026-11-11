# DTO del m�dulo editoriales (se implementan en ejercicios posteriores).
"""Contratos de editoriales."""

from pydantic import field_validator
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura

class EditorialCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=200)
    pais: str | None = Field(default=None, max_length=120)

class EditorialUpdate(Entrada):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    pais: str | None = Field(default=None, max_length=120)

    @field_validator("nombre")
    @classmethod
    def nombre_no_nulo(cls, valor):
        if valor is None:
            raise ValueError("El nombre no puede ser null.")
        return valor

class EditorialRead(Lectura):
    id: int
    nombre: str
    pais: str | None
