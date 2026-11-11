# DTO del m�dulo generos (se implementan en ejercicios posteriores).
"""Contratos de géneros."""
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura

class GeneroCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=200)

class GeneroRead(Lectura):
    id: int
    nombre: str
