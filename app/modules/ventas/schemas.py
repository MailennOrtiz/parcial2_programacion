# DTO del m�dulo ventas (se implementan en ejercicios posteriores).
"""Contratos inmutables de ventas."""
from datetime import datetime
from decimal import Decimal
from pydantic import field_validator
from sqlmodel import Field
from app.core.schemas import Entrada, Lectura
from app.modules.clientes.schemas import ClienteResumenRead

class RenglonCreate(Entrada):
    libro_id: int = Field(gt=0, le=2_147_483_647)
    cantidad: int = Field(gt=0, le=2_147_483_647)

class VentaCreate(Entrada):
    cliente_id: int = Field(gt=0, le=2_147_483_647)
    renglones: list[RenglonCreate] = Field(min_length=1)

    @field_validator("renglones")
    @classmethod
    def libros_no_repetidos(cls, renglones):
        ids = [r.libro_id for r in renglones]
        if len(ids) != len(set(ids)):
            raise ValueError("Un libro no puede repetirse en una venta.")
        return renglones

class RenglonRead(Lectura):
    libro_id: int
    titulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

class VentaRead(Lectura):
    id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteResumenRead
    renglones: list[RenglonRead]
