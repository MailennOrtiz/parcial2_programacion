"""Ingrediente.

diapositiva 6 — muchos a muchos: el otro extremo de la receta.
diapositiva 11 — `Ingrediente.productos`, navegación hacia la receta.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # Sólo para las anotaciones: evita el import circular en tiempo de ejecución
    # (productos/models.py importa Ingrediente).
    from app.modules.productos.models import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    """Un extremo del muchos a muchos. No tiene ninguna columna de productos:
    en qué productos va la cebolla se averigua en la tabla intermedia
    (`ProductoIngrediente`, en el módulo `productos`).
    """

    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    # ── Navegación: hacia las filas de la receta que lo usan ───────────────
    # Cada elemento es una fila de `ProductoIngrediente`, no un `Producto`:
    # así la cantidad viaja con él (`fila.cantidad`, `fila.producto`).
    # passive_deletes=True: si alguien borra un ingrediente, lo que pase con
    # sus filas de receta lo decide la base, no el ORM.
    productos: list["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente", passive_deletes=True
    )
