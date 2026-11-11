"""Pedido y sus líneas.

Parte 1 (cómo se guardan):
  Diapositiva 4 — la clave foránea.
  Diapositiva 4 — uno a muchos: la clave va del lado "muchos".
  Diapositiva 7 — composición: al borrar el pedido, se van sus líneas.
  Diapositiva 8 — la clave foránea se indexa (y acá, a propósito, no lo está).

Parte 2 (cómo se leen):
  Diapositiva 11 — `Relationship()` en los dos extremos, con `back_populates`.
  Diapositivas 12 a 14 — declarar no es cargar: ver `pedidos/service.py`.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # Sólo para las anotaciones: evita el import circular en tiempo de ejecución
    # (usuarios/models.py y productos/models.py también mencionan a estas clases).
    from app.modules.productos.models import Producto
    from app.modules.usuarios.models import Usuario


class Pedido(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")

    
    usuario: "Usuario" = Relationship(back_populates="pedidos")


    detalles: list["DetallePedido"] = Relationship(
        back_populates="pedido", cascade_delete=True, passive_deletes=True
    )


class DetallePedido(SQLModel, table=True):
    """Composición: el renglón no tiene sentido sin su ticket.

    `ondelete="CASCADE"` escribe un `ON DELETE CASCADE` en la clave foránea
    DE LA BASE: al borrar el pedido, la base borra sus líneas. La diferencia
    con `Producto.categoria_id` no está en que haya una clave foránea (las
    dos tablas la tienen): está en qué pasa al borrar.

    `producto_id` es otra clave foránea común, sin `ondelete`: un renglón
    apunta a un producto, pero no es "parte" de él.
    """

    __tablename__ = "detalle_pedido"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", ondelete="CASCADE")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int

    # ── diapositiva 11: la otra punta de `Pedido.detalles` ──────────
    pedido: Pedido = Relationship(back_populates="detalles")

    # El producto que nombra la línea. La otra punta es `Producto.detalles`.
    producto: "Producto" = Relationship(back_populates="detalles")
