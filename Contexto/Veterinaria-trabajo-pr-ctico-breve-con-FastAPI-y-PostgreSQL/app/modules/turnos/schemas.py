"""Reserva anidada sin importes y respuesta con precios históricos."""

from datetime import datetime
from decimal import Decimal

from pydantic import AwareDatetime
from sqlmodel import Field, SQLModel

from app.core.schemas import Entrada
from app.modules.mascotas.schemas import MascotaResumenRead


class TurnoPracticaCreate(Entrada):
    practica_id: int = Field(gt=0)


class TurnoCreate(Entrada):
    mascota_id: int = Field(gt=0)
    fecha: AwareDatetime
    motivo: str = Field(min_length=1, max_length=500)
    practicas: list[TurnoPracticaCreate] = Field(min_length=1)


class TurnoPracticaRead(SQLModel):
    practica_id: int
    nombre: str
    precio_unitario: Decimal


class TurnoRead(SQLModel):
    id: int
    fecha: datetime
    motivo: str
    total: Decimal
    mascota: MascotaResumenRead
    practicas: list[TurnoPracticaRead]
