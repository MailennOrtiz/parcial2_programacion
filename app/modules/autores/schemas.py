# DTO del m�dulo autores (se implementan en ejercicios posteriores).
"""Contratos de autores."""
from pydantic import field_validator
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura

class AutorCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=200)
    nacionalidad: str | None = Field(default=None, max_length=120)

class AutorUpdate(Entrada):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    nacionalidad: str | None = Field(default=None, max_length=120)

    @field_validator("nombre")
    @classmethod
    def nombre_no_nulo(cls, valor):
        if valor is None:
            raise ValueError("El nombre no puede ser null.")
        return valor

class AutorRead(Lectura):
    id: int
    nombre: str
    nacionalidad: str | None
