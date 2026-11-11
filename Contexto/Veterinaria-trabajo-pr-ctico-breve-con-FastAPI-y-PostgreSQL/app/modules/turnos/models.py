"""Turnos y sus prácticas reservadas, con precio propio de la relación."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota
    from app.modules.practicas.models import Practica


class Turno(SQLModel, table=True):
    __tablename__ = "turno"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_turno_total_no_negativo"),)

    id: int | None = Field(default=None, primary_key=True)
    mascota_id: int = Field(foreign_key="mascota.id", ondelete="RESTRICT", index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    motivo: str
    total: Decimal = Field(max_digits=12, decimal_places=2)

    mascota: "Mascota" = Relationship(back_populates="turnos")
    # Incluso si la colección está cargada, el ORM no debe emitir DELETE ni UPDATE
    # sobre sus filas. PostgreSQL las elimina con ON DELETE CASCADE.
    practicas: list["TurnoPractica"] = Relationship(
        back_populates="turno", passive_deletes="all"
    )


class TurnoPractica(SQLModel, table=True):
    __tablename__ = "turno_practica"
    __table_args__ = (
        CheckConstraint("precio_unitario > 0", name="ck_turno_practica_precio_positivo"),
    )

    # La PK compuesta ya indexa por turno_id; no necesita otro índice para esa FK.
    turno_id: int = Field(foreign_key="turno.id", ondelete="CASCADE", primary_key=True)
    practica_id: int = Field(
        foreign_key="practica.id", ondelete="RESTRICT", primary_key=True, index=True
    )
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)

    turno: Turno = Relationship(back_populates="practicas")
    practica: "Practica" = Relationship(back_populates="turnos")
