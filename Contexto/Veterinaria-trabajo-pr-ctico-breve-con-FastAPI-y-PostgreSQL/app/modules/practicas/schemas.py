"""Contratos del catálogo con dinero representado mediante Decimal."""

from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.core.schemas import Entrada


class PracticaCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=120)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class PracticaRead(SQLModel):
    id: int
    nombre: str
    precio: Decimal
