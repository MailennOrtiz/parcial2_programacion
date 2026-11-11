"""Altas, lecturas y paginación de mascotas, sin referencias circulares."""

from sqlmodel import Field, SQLModel

from app.core.schemas import Entrada
from app.modules.duenios.schemas import DuenioResumenRead


class MascotaCreate(Entrada):
    nombre: str = Field(min_length=1, max_length=120)
    especie: str = Field(min_length=1, max_length=80)
    duenio_id: int = Field(gt=0)


class MascotaResumenRead(SQLModel):
    id: int
    nombre: str
    especie: str


class MascotaRead(MascotaResumenRead):
    duenio_id: int


class MascotaDetalleRead(MascotaRead):
    duenio: DuenioResumenRead


class MascotasPage(SQLModel):
    items: list[MascotaRead]
    total: int
    page: int
    size: int
    pages: int
