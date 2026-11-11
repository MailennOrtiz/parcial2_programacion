"""Contrato de respuesta del laboratorio, sin persistencia propia."""

from sqlmodel import SQLModel


class StockRead(SQLModel):
    vacuna: str
    stock: int
