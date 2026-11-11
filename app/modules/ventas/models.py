"""Ventas de la librería, sus renglones y el aviso posterior."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import Libro


class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_venta_total_no_negativo"),)

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    total: Decimal = Field(max_digits=12, decimal_places=2)

    cliente: "Cliente" = Relationship(back_populates="ventas")
    renglones: list["RenglonVenta"] = Relationship(
        back_populates="venta", passive_deletes="all"
    )


class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_renglon_venta_cantidad_positiva"),
        CheckConstraint("precio_unitario > 0", name="ck_renglon_venta_precio_positivo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)

    venta: "Venta" = Relationship(back_populates="renglones")
    libro: "Libro" = Relationship(back_populates="renglones")