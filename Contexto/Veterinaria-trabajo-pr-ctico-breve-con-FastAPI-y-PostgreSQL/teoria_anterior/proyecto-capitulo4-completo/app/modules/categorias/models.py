"""Categoría.

Diapositiva 7 — agregación: la categoría es la góndola.
Diapositiva 11 — `Categoria.productos`, la otra punta de `Producto.categoria`.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # Sólo para las anotaciones: evita el import circular en tiempo de ejecución
    # (productos/models.py importa Categoria).
    from app.modules.productos.models import Producto


class Categoria(SQLModel, table=True):
    """La góndola. Si se saca, las latas siguen existiendo.

    Igual que `Usuario`, no tiene ninguna columna de productos: es cada producto el que anota en
    qué categoría está (`Producto.categoria_id`).
    """

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)

    # ── Navegación: la otra punta de `Producto.categoria` ──────────────────
    # No agrega columnas: `categoria.productos` es una consulta que el ORM
    # sabe armar (SELECT ... FROM producto WHERE categoria_id = ...).
    #
    # passive_deletes="all" — qué pasa al borrar la categoría lo decide LA
    # BASE (el ON DELETE de `producto.categoria_id`), no el ORM. Sin esto, al
    # borrar una categoría el ORM iría a buscar sus productos y les vaciaría
    # `categoria_id` él mismo (UPDATE producto SET categoria_id = NULL) antes
    # de que la base pudiera decir nada: el RESTRICT de la diapositiva 7 nunca
    # se vería y la góndola se sacaría con las latas adentro. Con "all", el
    # ORM no toca los productos ni siquiera si los tiene en memoria.
    productos: list["Producto"] = Relationship(
        back_populates="categoria", passive_deletes="all"
    )
