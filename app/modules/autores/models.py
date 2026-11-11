"""Autores del catálogo de la librería."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import LibroAutor


class Autor(SQLModel, table=True):
    __tablename__ = "autor"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: str | None = None

    autorias: list["LibroAutor"] = Relationship(back_populates="autor")