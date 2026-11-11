"""Catálogo de prácticas; los precios históricos viven en TurnoPractica."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.turnos.models import TurnoPractica


class Practica(SQLModel, table=True):
    __tablename__ = "practica"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_practica_nombre"),
        CheckConstraint("precio > 0", name="ck_practica_precio_positivo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    precio: Decimal = Field(max_digits=10, decimal_places=2)

    turnos: list["TurnoPractica"] = Relationship(
        back_populates="practica", passive_deletes="all"
    )
