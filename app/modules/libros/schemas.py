# DTO del m�dulo libros (se implementan en ejercicios posteriores).
"""Contratos de libros y autorías."""
from decimal import Decimal
from typing import Literal
from pydantic import field_validator
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura
from app.modules.editoriales.schemas import EditorialRead
from app.modules.generos.schemas import GeneroRead
from app.modules.autores.schemas import AutorRead

class AutoriaCreate(Entrada):
    autor_id: int = Field(gt=0)
    rol: Literal["autor", "coautor", "traductor", "ilustrador"]
    orden: int = Field(ge=1)

class LibroCreate(Entrada):
    isbn: str = Field(min_length=1, max_length=50)
    titulo: str = Field(min_length=1, max_length=250)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    editorial_id: int = Field(gt=0)
    genero_id: int | None = Field(default=None, gt=0)
    autores: list[AutoriaCreate] = Field(default_factory=list)

class LibroUpdate(Entrada):
    isbn: str | None = Field(default=None, min_length=1, max_length=50)
    titulo: str | None = Field(default=None, min_length=1, max_length=250)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    editorial_id: int | None = Field(default=None, gt=0)
    genero_id: int | None = Field(default=None, gt=0)

    @field_validator("isbn", "titulo", "precio", "stock", "editorial_id")
    @classmethod
    def campos_no_nulos(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser null.")
        return valor

class LibroResumenRead(Lectura):
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial: EditorialRead
    genero: GeneroRead | None

class AutoriaRead(Lectura):
    autor: AutorRead
    rol: str
    orden: int

class LibroRead(LibroResumenRead):
    autores: list[AutoriaRead]

class LibroDeAutorRead(Lectura):
    libro: LibroResumenRead
    rol: str
    orden: int
